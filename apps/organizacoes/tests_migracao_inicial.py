import importlib

from django.apps import apps
from django.test import TestCase
from django.utils import timezone

from apps.catalogo.models import Catalogo
from apps.clientes.models import Cliente
from apps.contas.models.choices import TipoUsuario
from apps.ordens_servico.models import OrdemServico, Servico
from apps.organizacoes.models import Funcao, MembroSetor, Setor
from apps.organizacoes.permissoes import (
    PERMISSOES_POR_TIPO_USUARIO, Permissao, permissoes_do_usuario, tem_permissao,
)
from apps.organizacoes.tests_permissoes import criar_usuario

migracao = importlib.import_module('apps.organizacoes.migrations.0013_cria_setores_funcoes_e_vinculos_iniciais')


class MigracaoInicialTestCase(TestCase):
    def test_cria_os_cinco_setores(self):
        self.assertEqual(
            set(Setor.objects.values_list('nome', flat=True)),
            {'Diretoria', 'Comercial', 'Segurança do Trabalho', 'Financeiro', 'Administrativo'},
        )

    def test_funcoes_concedem_o_mesmo_que_o_tipo_de_usuario(self):
        for tipo, (_, nome_funcao, _) in migracao.MAPEAMENTO.items():
            funcao = Funcao.objects.get(nome=nome_funcao)
            self.assertEqual(set(funcao.codigos_permissao), set(PERMISSOES_POR_TIPO_USUARIO[tipo]), tipo)

    def test_vincula_cada_usuario_ao_setor_da_sua_area_sem_mudar_o_acesso(self):
        usuarios = {tipo: criar_usuario(tipo) for tipo in TipoUsuario}
        acesso_antes = {tipo: permissoes_do_usuario(u) for tipo, u in usuarios.items()}

        migracao.criar_estrutura_e_vincular(apps, None)

        for tipo, usuario in usuarios.items():
            nome_setor, nome_funcao, _ = migracao.MAPEAMENTO[tipo]
            vinculo = MembroSetor.objects.get(usuario=usuario)
            self.assertEqual((vinculo.setor.nome, vinculo.funcao.nome), (nome_setor, nome_funcao))
            usuario.__dict__.pop('_perfil_de_acesso', None)
            self.assertEqual(permissoes_do_usuario(usuario), acesso_antes[tipo], tipo)

    def test_rodar_de_novo_nao_duplica(self):
        criar_usuario(TipoUsuario.TECNICO)
        migracao.criar_estrutura_e_vincular(apps, None)
        migracao.criar_estrutura_e_vincular(apps, None)

        self.assertEqual(MembroSetor.objects.count(), 1)
        self.assertEqual(Setor.objects.count(), 5)


class DiretoriaAtuaEmTodosOsSetoresTestCase(TestCase):
    def setUp(self):
        self.diretor = criar_usuario(TipoUsuario.DIRETOR)
        self.gestor_tecnico = criar_usuario(TipoUsuario.GESTOR_TECNICO)
        migracao.criar_estrutura_e_vincular(apps, None)
        for usuario in (self.diretor, self.gestor_tecnico):
            usuario.__dict__.pop('_perfil_de_acesso', None)
        self.seguranca = Setor.objects.get(nome='Segurança do Trabalho')
        self.servico = Servico.objects.create(
            ordem_servico=OrdemServico.objects.create(
                cliente=Cliente.objects.create(nome='Cliente'), data_venda=timezone.localdate(), valor=0,
            ),
            descricao='PGR', catalogo=Catalogo.objects.create(nome='PGR', setor=self.seguranca),
        )

    def test_diretor_distribui_tarefas_num_setor_em_que_nao_tem_vinculo(self):
        self.assertTrue(tem_permissao(self.diretor, Permissao.TAREFAS_DISTRIBUIR, self.servico.setor_id))

    def test_gestor_tecnico_distribui_so_em_seguranca_do_trabalho(self):
        comercial = Setor.objects.get(nome='Comercial')

        self.assertTrue(tem_permissao(self.gestor_tecnico, Permissao.TAREFAS_DISTRIBUIR, self.seguranca))
        self.assertFalse(tem_permissao(self.gestor_tecnico, Permissao.TAREFAS_DISTRIBUIR, comercial))
