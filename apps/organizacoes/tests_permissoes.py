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


class RegistroDeCobrancaTestCase(APITestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome='Cliente Cobranca')
        self.ordem = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=timezone.localdate(), valor=100, cobranca_imediata=True,
        )
        self.url = reverse('ordens-servico-registrar-cobranca', args=[self.ordem.id])

    def test_financeiro_registra_cobranca(self):
        self.client.force_authenticate(user=criar_usuario(TipoUsuario.FINANCEIRO))

        response = self.client.patch(self.url, {'numero_nf': 123})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ordem.refresh_from_db()
        self.assertTrue(self.ordem.cobranca_realizada)

    def test_comercial_nao_registra_cobranca(self):
        self.client.force_authenticate(user=criar_usuario(TipoUsuario.COMERCIAL))

        response = self.client.patch(self.url, {'numero_nf': 123})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.ordem.refresh_from_db()
        self.assertFalse(self.ordem.cobranca_realizada)

    def test_edicao_generica_da_os_ignora_campos_de_cobranca(self):
        self.client.force_authenticate(user=criar_usuario(TipoUsuario.FINANCEIRO))

        self.client.patch(
            reverse('ordens-servico-detail', args=[self.ordem.id]),
            {'cobranca_realizada': True, 'numero_nf': 999},
        )

        self.ordem.refresh_from_db()
        self.assertFalse(self.ordem.cobranca_realizada)
        self.assertIsNone(self.ordem.numero_nf)

    def test_tecnico_nao_registra_cobranca_de_os_operacional(self):
        from apps.catalogo.models import CatalogoOperacional
        from apps.ordens_servico.models import OrdemServicoOperacional
        tecnico = criar_usuario(TipoUsuario.TECNICO)
        oso = OrdemServicoOperacional.objects.create(
            cliente=self.cliente, responsavel=tecnico, revisao_cliente=True, status='finalizada',
            catalogo_operacional=CatalogoOperacional.objects.create(nome='Revisão'),
        )
        self.client.force_authenticate(user=tecnico)

        response = self.client.patch(
            reverse('ordens-servico-operacionais-registrar-cobranca', args=[oso.id]), {'numero_nf': '1'},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        oso.refresh_from_db()
        self.assertFalse(oso.cobranca_realizada)


class OcultacaoDeValoresTestCase(APITestCase):
    def setUp(self):
        self.ordem = OrdemServico.objects.create(
            cliente=Cliente.objects.create(nome='Cliente Valores'), data_venda=timezone.localdate(),
            valor=1500, forma_pagamento='pix', quantidade_parcelas=3,
        )
        self.detalhe = reverse('ordens-servico-detail', args=[self.ordem.id])

    def test_administrativo_nao_recebe_valores_na_lista_nem_no_detalhe(self):
        self.client.force_authenticate(user=criar_usuario(TipoUsuario.ADMINISTRATIVO))

        lista = self.client.get(reverse('ordens-servico-list'))
        detalhe = self.client.get(self.detalhe)

        itens = lista.data['results'] if isinstance(lista.data, dict) else lista.data
        for campo in ('valor', 'forma_pagamento', 'quantidade_parcelas'):
            self.assertNotIn(campo, itens[0])
            self.assertNotIn(campo, detalhe.data)

    def test_financeiro_recebe_valores(self):
        self.client.force_authenticate(user=criar_usuario(TipoUsuario.FINANCEIRO))

        detalhe = self.client.get(self.detalhe)

        self.assertEqual(detalhe.data['valor'], '1500.00')

    def test_edicao_sem_permissao_nao_zera_o_valor(self):
        self.client.force_authenticate(user=criar_usuario(TipoUsuario.ADMINISTRATIVO))

        # O formulário do frontend reenvia valor e forma de pagamento mesmo sem exibi-los.
        response = self.client.patch(self.detalhe, {
            'valor': '0.00', 'forma_pagamento': '', 'quantidade_parcelas': '', 'observacao': 'ajuste',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.valor, 1500)
        self.assertEqual(self.ordem.forma_pagamento, 'pix')
        self.assertEqual(self.ordem.observacao, 'ajuste')

    def test_criacao_sem_permissao_aceita_o_valor(self):
        self.client.force_authenticate(user=criar_usuario(TipoUsuario.ADMINISTRATIVO))

        response = self.client.post(reverse('ordens-servico-list'), {
            'cliente': self.ordem.cliente_id, 'data_venda': str(timezone.localdate()), 'valor': '800.00',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('valor', response.data)
        self.assertEqual(OrdemServico.objects.get(id=response.data['id']).valor, 800)


class VisibilidadeDeServicosTestCase(APITestCase):
    def setUp(self):
        self.tecnico = criar_usuario(TipoUsuario.TECNICO)
        ordem = OrdemServico.objects.create(
            cliente=Cliente.objects.create(nome='Cliente Visibilidade'), data_venda=timezone.localdate(), valor=0,
        )
        self.meu = Servico.objects.create(ordem_servico=ordem, descricao='meu')
        self.outro = Servico.objects.create(ordem_servico=ordem, descricao='de outro')
        Tarefa.objects.create(servico=self.meu, responsavel=self.tecnico)
        Tarefa.objects.create(servico=self.meu, responsavel=self.tecnico)
        Tarefa.objects.create(servico=self.outro, responsavel=criar_usuario(TipoUsuario.TECNICO))

    def ids(self, response):
        itens = response.data['results'] if isinstance(response.data, dict) else response.data
        return [s['id'] for s in itens]

    def test_tecnico_ve_so_servicos_em_que_tem_tarefa(self):
        self.client.force_authenticate(user=self.tecnico)

        response = self.client.get(reverse('servicos-list'))
        detalhe_de_outro = self.client.get(reverse('servicos-detail', args=[self.outro.id]))

        self.assertEqual(self.ids(response), [self.meu.id])
        self.assertEqual(detalhe_de_outro.status_code, status.HTTP_404_NOT_FOUND)

    def test_gestor_tecnico_ve_todos(self):
        self.client.force_authenticate(user=criar_usuario(TipoUsuario.GESTOR_TECNICO))

        response = self.client.get(reverse('servicos-list'))

        self.assertCountEqual(self.ids(response), [self.meu.id, self.outro.id])
