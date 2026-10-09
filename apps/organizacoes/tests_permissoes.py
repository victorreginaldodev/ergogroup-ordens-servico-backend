from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.clientes.models import Cliente
from apps.contas.models import Usuario
from apps.contas.models.choices import TipoUsuario
from apps.ordens_servico.models import OrdemServico, Servico, Tarefa
from apps.organizacoes.permissoes import (
    PERMISSOES_POR_TIPO_USUARIO, Permissao, permissoes_do_usuario, tem_permissao,
)


def criar_usuario(tipo, **extra):
    return Usuario.objects.create_user(
        username=f'{tipo}_{Usuario.objects.count()}', email=f'{tipo}{Usuario.objects.count()}@ergogroup.test',
        password='senha-teste-123', nome_completo=f'Usuario {tipo}', tipo_usuario=tipo, **extra,
    )


class CatalogoDePermissoesTestCase(APITestCase):
    def test_todo_tipo_de_usuario_tem_permissoes_mapeadas(self):
        self.assertEqual(set(PERMISSOES_POR_TIPO_USUARIO), set(TipoUsuario))

    def test_diretor_e_gestor_comercial_tem_todas(self):
        for tipo in (TipoUsuario.DIRETOR, TipoUsuario.GESTOR_COMERCIAL):
            self.assertEqual(permissoes_do_usuario(criar_usuario(tipo)), frozenset(Permissao))

    def test_superusuario_tem_todas(self):
        usuario = criar_usuario(TipoUsuario.TECNICO, is_superuser=True)
        self.assertEqual(permissoes_do_usuario(usuario), frozenset(Permissao))

    def test_usuario_inativo_nao_tem_permissoes(self):
        usuario = criar_usuario(TipoUsuario.DIRETOR, is_active=False)
        self.assertEqual(permissoes_do_usuario(usuario), frozenset())

    def test_tecnico_nao_ve_todas_as_os_nem_valores(self):
        tecnico = criar_usuario(TipoUsuario.TECNICO)
        self.assertFalse(tem_permissao(tecnico, Permissao.OS_VER_TODAS))
        self.assertFalse(tem_permissao(tecnico, Permissao.FINANCEIRO_VER_VALORES))

    def test_administrativo_nao_ve_valores(self):
        for tipo in (TipoUsuario.ADMINISTRATIVO, TipoUsuario.GESTOR_ADMINISTRATIVO, TipoUsuario.SUB_GESTOR_TECNICO):
            self.assertFalse(tem_permissao(criar_usuario(tipo), Permissao.FINANCEIRO_VER_VALORES))


class GestorComercialComoDiretorTestCase(APITestCase):
    def test_gestor_comercial_muda_status_de_tarefa_de_outra_pessoa(self):
        gestor_comercial = criar_usuario(TipoUsuario.GESTOR_COMERCIAL)
        tecnico = criar_usuario(TipoUsuario.TECNICO)
        ordem = OrdemServico.objects.create(
            cliente=Cliente.objects.create(nome='Cliente'), data_venda=timezone.localdate(), valor=0,
        )
        tarefa = Tarefa.objects.create(
            servico=Servico.objects.create(ordem_servico=ordem, descricao='s'), responsavel=tecnico,
        )
        self.client.force_authenticate(user=gestor_comercial)

        response = self.client.patch(reverse('tarefas-detail', args=[tarefa.id]), {'status': 'em_andamento'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EdicaoDoProprioCadastroTestCase(APITestCase):
    def setUp(self):
        self.tecnico = criar_usuario(TipoUsuario.TECNICO)
        self.client.force_authenticate(user=self.tecnico)
        self.url = reverse('usuarios-detail', args=[self.tecnico.id])

    def test_tecnico_nao_consegue_virar_diretor(self):
        self.client.patch(self.url, {'tipo_usuario': TipoUsuario.DIRETOR})

        self.tecnico.refresh_from_db()
        self.assertEqual(self.tecnico.tipo_usuario, TipoUsuario.TECNICO)

    def test_tecnico_nao_altera_o_proprio_status(self):
        self.client.patch(self.url, {'ativo': False})

        self.tecnico.refresh_from_db()
        self.assertTrue(self.tecnico.ativo)

    def test_tecnico_edita_o_proprio_nome(self):
        response = self.client.patch(self.url, {'nome_completo': 'Nome Novo'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tecnico.refresh_from_db()
        self.assertEqual(self.tecnico.nome_completo, 'Nome Novo')


class GestaoDaDiretoriaTestCase(APITestCase):
    def setUp(self):
        self.gestor_tecnico = criar_usuario(TipoUsuario.GESTOR_TECNICO)
        self.diretor = criar_usuario(TipoUsuario.DIRETOR)
        self.tecnico = criar_usuario(TipoUsuario.TECNICO)

    def payload_novo_usuario(self, tipo):
        return {
            'email': f'novo.{tipo}@ergogroup.test', 'username': f'novo_{tipo}', 'nome_completo': 'Novo',
            'tipo_usuario': tipo, 'ativo': True,
            'password': 'Senha-forte-123', 'password_confirmacao': 'Senha-forte-123',
        }

    def test_gestor_nao_diretoria_cria_tecnico(self):
        self.client.force_authenticate(user=self.gestor_tecnico)

        response = self.client.post(reverse('usuarios-list'), self.payload_novo_usuario(TipoUsuario.TECNICO))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_gestor_nao_diretoria_nao_cria_diretor(self):
        self.client.force_authenticate(user=self.gestor_tecnico)

        response = self.client.post(reverse('usuarios-list'), self.payload_novo_usuario(TipoUsuario.DIRETOR))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Usuario.objects.filter(email='novo.diretor@ergogroup.test').exists())

    def test_gestor_nao_diretoria_nao_promove_a_diretor(self):
        self.client.force_authenticate(user=self.gestor_tecnico)

        response = self.client.patch(
            reverse('usuarios-detail', args=[self.tecnico.id]), {'tipo_usuario': TipoUsuario.GESTOR_COMERCIAL},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.tecnico.refresh_from_db()
        self.assertEqual(self.tecnico.tipo_usuario, TipoUsuario.TECNICO)

    def test_gestor_nao_diretoria_nao_desativa_nem_exclui_diretor(self):
        self.client.force_authenticate(user=self.gestor_tecnico)

        desativar = self.client.patch(reverse('usuarios-desativar', args=[self.diretor.id]))
        excluir = self.client.delete(reverse('usuarios-detail', args=[self.diretor.id]))

        self.assertEqual(desativar.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(excluir.status_code, status.HTTP_403_FORBIDDEN)
        self.diretor.refresh_from_db()
        self.assertTrue(self.diretor.ativo)

    def test_diretor_cria_diretor(self):
        self.client.force_authenticate(user=self.diretor)

        response = self.client.post(reverse('usuarios-list'), self.payload_novo_usuario(TipoUsuario.DIRETOR))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
