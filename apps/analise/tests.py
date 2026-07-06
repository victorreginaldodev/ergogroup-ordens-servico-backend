from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.clientes.models import Cliente
from apps.contas.models import Usuario
from apps.contas.models.choices import TipoUsuario
from apps.ordens_servico.models import OrdemServico
from apps.ordens_servico.models import Servico
from apps.catalogo.models.catalogo import Catalogo
from apps.ordens_servico.models.servico import StatusServico
from apps.ordens_servico.models import Tarefa, OrdemServicoOperacional
from apps.catalogo.models import CatalogoOperacional
from apps.ordens_servico.models.tarefa import StatusTarefa
from apps.ordens_servico.models.ordem_servico_operacional import StatusOrdemServicoOperacional


PERFIS_SEM_VALORES = [
    TipoUsuario.SUB_GESTOR_TECNICO,
    TipoUsuario.TECNICO,
    TipoUsuario.GESTOR_ADMINISTRATIVO,
    TipoUsuario.ADMINISTRATIVO,
]


class AnaliseTestCase(APITestCase):
    def setUp(self):
        self.hoje = timezone.localdate()

        self.usuarios = {
            tipo: Usuario.objects.create_user(
                username=f'usuario_{tipo}',
                email=f'{tipo}@ergogroup.test',
                password='senha-teste-123',
                nome_completo=f'Usuario {tipo}',
                tipo_usuario=tipo,
            )
            for tipo in TipoUsuario.values
        }
        self.tecnico = self.usuarios[TipoUsuario.TECNICO]
        self.outro_tecnico = Usuario.objects.create_user(
            username='outro_tecnico',
            email='outro_tecnico@ergogroup.test',
            password='senha-teste-123',
            nome_completo='Outro Tecnico',
            tipo_usuario=TipoUsuario.TECNICO,
        )

        self.cliente = Cliente.objects.create(nome='Cliente Financeiro')

        # OS financeiras "soltas" (sem servicos/tarefas), para testar somas e redação de valores.
        self.os_cobranca_realizada = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=self.hoje, valor=1000,
            cobranca_realizada=True, liberada_para_cobranca=True,
        )
        self.os_liberada = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=self.hoje, valor=500,
            cobranca_realizada=False, liberada_para_cobranca=True,
        )
        self.os_sem_liberacao = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=self.hoje, valor=300,
            cobranca_realizada=False, liberada_para_cobranca=False,
        )

        # Cadeia OS -> Servico -> Tarefa para indicadores de produtividade/tempo.
        catalogo = Catalogo.objects.create(nome='Catalogo Teste')
        self.os_chain = OrdemServico.objects.create(
            cliente=self.cliente,
            data_venda=self.hoje - timedelta(days=5),
            valor=0,
        )
        self.servico_chain = Servico.objects.create(
            ordem_servico=self.os_chain,
            catalogo=catalogo,
            descricao='Servico de teste',
        )
        self.tarefa_chain = Tarefa.objects.create(
            servico=self.servico_chain,
            responsavel=self.tecnico,
            descricao='Tarefa de teste',
            status=StatusTarefa.CONCLUIDA,
        )
        # Backdata o início (e a criação, para não afetar o tempo de resposta)
        # da tarefa para gerar uma duração mensurável, e repropaga a
        # sincronização (data_termino é mantida pelo proprio fluxo).
        Tarefa.objects.filter(pk=self.tarefa_chain.pk).update(
            data_inicio=self.hoje - timedelta(days=3),
            criada_em=timezone.now() - timedelta(days=3),
        )
        self.servico_chain.refresh_from_db()
        self.servico_chain.sincronizar_status_e_rastreio()

        # Segunda cadeia, para validar que um técnico só vê a própria linha.
        self.os_chain_outro = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=self.hoje, valor=0,
        )
        self.servico_chain_outro = Servico.objects.create(
            ordem_servico=self.os_chain_outro,
            catalogo=catalogo,
            descricao='Servico de outro tecnico',
        )
        Tarefa.objects.create(
            servico=self.servico_chain_outro,
            responsavel=self.outro_tecnico,
            descricao='Tarefa de outro tecnico',
            status=StatusTarefa.CONCLUIDA,
        )

        catalogo_operacional = CatalogoOperacional.objects.create(nome='Catalogo Operacional Teste')
        self.oso = OrdemServicoOperacional.objects.create(
            cliente=self.cliente,
            catalogo_operacional=catalogo_operacional,
            responsavel=self.tecnico,
            data_recebimento=self.hoje,
            status=StatusOrdemServicoOperacional.FINALIZADA,
        )

        # Carga de trabalho atual (WIP) do tecnico: uma tarefa e uma OS operacional em andamento.
        os_wip = OrdemServico.objects.create(cliente=self.cliente, data_venda=self.hoje, valor=0)
        servico_wip = Servico.objects.create(
            ordem_servico=os_wip, catalogo=catalogo, descricao='Servico em andamento',
        )
        self.tarefa_wip = Tarefa.objects.create(
            servico=servico_wip, responsavel=self.tecnico,
            descricao='Tarefa em andamento', status=StatusTarefa.EM_ANDAMENTO,
        )
        self.oso_wip = OrdemServicoOperacional.objects.create(
            cliente=self.cliente, catalogo_operacional=catalogo_operacional, responsavel=self.tecnico,
            data_recebimento=self.hoje, status=StatusOrdemServicoOperacional.EM_ANDAMENTO,
        )

        # Tarefa que esperou 4 dias antes de ser iniciada, para medir o tempo de resposta.
        os_lead_time = OrdemServico.objects.create(cliente=self.cliente, data_venda=self.hoje, valor=0)
        servico_lead_time = Servico.objects.create(
            ordem_servico=os_lead_time, catalogo=catalogo, descricao='Servico com espera',
        )
        self.tarefa_lead_time = Tarefa.objects.create(
            servico=servico_lead_time, responsavel=self.tecnico,
            descricao='Tarefa com espera', status=StatusTarefa.EM_ANDAMENTO,
        )
        Tarefa.objects.filter(pk=self.tarefa_lead_time.pk).update(
            criada_em=timezone.now() - timedelta(days=4),
        )

        # Tarefa e servico cancelados, para a taxa de cancelamento.
        os_cancelamento = OrdemServico.objects.create(cliente=self.cliente, data_venda=self.hoje, valor=0)
        servico_tarefa_cancelada = Servico.objects.create(
            ordem_servico=os_cancelamento, catalogo=catalogo, descricao='Servico da tarefa cancelada',
        )
        self.tarefa_cancelada = Tarefa.objects.create(
            servico=servico_tarefa_cancelada, responsavel=self.tecnico,
            descricao='Tarefa cancelada', status=StatusTarefa.CANCELADA,
        )
        self.servico_cancelado = Servico.objects.create(
            ordem_servico=os_cancelamento, catalogo=catalogo,
            descricao='Servico cancelado', status=StatusServico.CANCELADO,
        )

    def _login(self, usuario):
        self.client.force_authenticate(user=usuario)


class AnaliseDadosViewTests(AnaliseTestCase):
    url = reverse('analise-dados')

    def test_gestor_ve_vendas_e_clientes(self):
        self._login(self.usuarios[TipoUsuario.GESTOR_FINANCEIRO])
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('vendas_por_mes', response.data['ordens_servico'])
        self.assertIn('clientes', response.data)

        total_vendas = sum(item['total'] for item in response.data['ordens_servico']['vendas_por_mes'])
        self.assertEqual(total_vendas, 1800)

        mais_vendas = response.data['clientes']['mais_vendas']
        self.assertEqual(len(mais_vendas), 1)
        self.assertEqual(mais_vendas[0]['total_valor_vendas'], 1800)

        mais_cobranca = response.data['clientes']['mais_cobranca']
        self.assertEqual(mais_cobranca[0]['total_valor_cobrado'], 1000)

    def test_perfis_restritos_nao_veem_valores(self):
        for tipo in PERFIS_SEM_VALORES:
            with self.subTest(tipo=tipo):
                self._login(self.usuarios[tipo])
                response = self.client.get(self.url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertNotIn('vendas_por_mes', response.data['ordens_servico'])
                self.assertNotIn('clientes', response.data)
                # Contagens operacionais continuam visiveis.
                self.assertEqual(response.data['ordens_servico']['total'], OrdemServico.objects.count())

    def test_requer_autenticacao(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FinanceiroKPIsViewTests(AnaliseTestCase):
    url = reverse('analise-financeiro-kpis')

    def test_perfis_restritos_recebem_403(self):
        for tipo in PERFIS_SEM_VALORES:
            with self.subTest(tipo=tipo):
                self._login(self.usuarios[tipo])
                response = self.client.get(self.url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_perfil_autorizado_recebe_totais_corretos(self):
        self._login(self.usuarios[TipoUsuario.GESTOR_FINANCEIRO])
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_cobrado'], 1000)
        self.assertEqual(response.data['total_para_cobrar'], 500)
        self.assertEqual(response.data['total_sem_liberacao'], 300)


class ProdutividadeViewTests(AnaliseTestCase):
    url = reverse('analise-produtividade')

    def test_tempos_medios(self):
        self._login(self.usuarios[TipoUsuario.GESTOR_TECNICO])
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('visitas_tecnicas_por_mes', response.data)

        # os_chain encerra em 5 dias e os_chain_outro em 0 dias -> media 2.5.
        # servico_chain encerra em 3 dias e servico_chain_outro em 0 dias -> media 1.5.
        # tarefas com data_inicio: 0, 0, 0 (chain/outro/wip) e 4 (lead_time) -> media 1.0.
        tempos = response.data['tempos_medios']
        self.assertEqual(tempos['os_criacao_para_encerramento_dias'], 2.5)
        self.assertEqual(tempos['os_criacao_para_conclusao_dias'], 1.0)
        self.assertEqual(tempos['servicos_inicio_para_fim_dias'], 1.5)
        self.assertEqual(tempos['tarefa_criacao_para_inicio_dias'], 1.0)

    def test_taxa_cancelamento(self):
        self._login(self.usuarios[TipoUsuario.GESTOR_TECNICO])
        response = self.client.get(self.url)

        taxa = response.data['taxa_cancelamento']
        self.assertEqual(taxa['tarefas']['canceladas'], 1)
        self.assertEqual(taxa['tarefas']['total'], Tarefa.objects.count())
        self.assertEqual(taxa['servicos']['canceladas'], 1)
        self.assertEqual(taxa['servicos']['total'], Servico.objects.count())

    def test_gestor_ve_todos_os_tecnicos(self):
        self._login(self.usuarios[TipoUsuario.GESTOR_TECNICO])
        response = self.client.get(self.url)

        ids = {item['tecnico_id'] for item in response.data['por_tecnico']}
        self.assertIn(self.tecnico.id, ids)
        self.assertIn(self.outro_tecnico.id, ids)

    def test_tecnico_ve_apenas_a_propria_linha_com_carga_de_trabalho(self):
        self._login(self.tecnico)
        response = self.client.get(self.url)

        por_tecnico = response.data['por_tecnico']
        self.assertEqual(len(por_tecnico), 1)
        linha = por_tecnico[0]
        self.assertEqual(linha['tecnico_id'], self.tecnico.id)
        self.assertEqual(linha['tarefas_concluidas'], 1)
        self.assertEqual(linha['mini_os_concluidas'], 1)
        self.assertEqual(linha['tempo_medio_tarefa_dias'], 3.0)
        # tarefa_wip e tarefa_lead_time estao em andamento; oso_wip tambem.
        self.assertEqual(linha['tarefas_em_aberto'], 2)
        self.assertEqual(linha['mini_os_em_aberto'], 1)
