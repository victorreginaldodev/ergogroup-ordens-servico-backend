from datetime import timedelta
from decimal import Decimal

from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.clientes.models import Cliente
from apps.contas.models import Usuario
from apps.contas.models.choices import TipoUsuario
from apps.catalogo.models import Catalogo, CatalogoOperacional, Complexidade
from apps.ordens_servico.models import (
    OrdemServico, OrdemServicoOperacional, Servico, Tarefa, Prioridade,
)
from apps.ordens_servico.models.ordem_servico_operacional import StatusOrdemServicoOperacional
from apps.ordens_servico.models.tarefa import StatusTarefa


class ProdutividadeModelTestCase(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='tecnico_teste',
            email='tecnico@ergogroup.test',
            password='senha-teste-123',
            nome_completo='Tecnico Teste',
            tipo_usuario=TipoUsuario.TECNICO,
        )
        self.cliente = Cliente.objects.create(nome='Cliente Teste')
        self.catalogo = Catalogo.objects.create(
            nome='Catalogo Teste', horas_estimadas=Decimal('5.50'), complexidade=Complexidade.ALTA,
        )
        self.ordem_servico = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=timezone.localdate(), valor=0, prioridade=Prioridade.ALTA,
        )

    def test_horas_estimadas_efetivas_cai_no_catalogo_quando_sem_override(self):
        servico = Servico.objects.create(
            ordem_servico=self.ordem_servico, catalogo=self.catalogo, descricao='sem override',
        )
        self.assertEqual(servico.horas_estimadas_efetivas, Decimal('5.50'))
        self.assertEqual(servico.complexidade_efetiva, Complexidade.ALTA)

    def test_horas_estimadas_efetivas_override_tem_prioridade_sobre_catalogo(self):
        servico = Servico.objects.create(
            ordem_servico=self.ordem_servico, catalogo=self.catalogo, descricao='com override',
            horas_estimadas=Decimal('2.00'), complexidade=Complexidade.BAIXA,
        )
        self.assertEqual(servico.horas_estimadas_efetivas, Decimal('2.00'))
        self.assertEqual(servico.complexidade_efetiva, Complexidade.BAIXA)

    def test_horas_estimadas_efetivas_none_sem_catalogo_e_sem_override(self):
        servico = Servico.objects.create(
            ordem_servico=self.ordem_servico, catalogo=None, descricao='sem catalogo',
        )
        self.assertIsNone(servico.horas_estimadas_efetivas)
        self.assertIsNone(servico.complexidade_efetiva)

    def test_tarefa_horas_estimadas_efetivas_cai_no_servico_quando_sem_override(self):
        servico = Servico.objects.create(
            ordem_servico=self.ordem_servico, catalogo=self.catalogo, descricao='servico',
        )
        tarefa = Tarefa.objects.create(servico=servico, responsavel=self.usuario, descricao='sem override')
        self.assertEqual(tarefa.horas_estimadas_efetivas, Decimal('5.50'))

    def test_tarefa_horas_estimadas_efetivas_override_tem_prioridade_sobre_servico(self):
        servico = Servico.objects.create(
            ordem_servico=self.ordem_servico, catalogo=self.catalogo, descricao='servico',
            horas_estimadas=Decimal('3.00'),
        )
        tarefa = Tarefa.objects.create(
            servico=servico, responsavel=self.usuario, descricao='com override', horas_estimadas=Decimal('1.00'),
        )
        self.assertEqual(tarefa.horas_estimadas_efetivas, Decimal('1.00'))

    def test_tarefa_horas_estimadas_efetivas_none_quando_nada_definido(self):
        servico = Servico.objects.create(
            ordem_servico=self.ordem_servico, catalogo=None, descricao='sem catalogo',
        )
        tarefa = Tarefa.objects.create(servico=servico, responsavel=self.usuario, descricao='sem nada')
        self.assertIsNone(tarefa.horas_estimadas_efetivas)


class HerancaPrioridadeSerializerTestCase(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='tecnico_heranca',
            email='heranca@ergogroup.test',
            password='senha-teste-123',
            nome_completo='Tecnico Heranca',
            tipo_usuario=TipoUsuario.TECNICO,
        )
        self.cliente = Cliente.objects.create(nome='Cliente Heranca')
        self.ordem_servico = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=timezone.localdate(), valor=0, prioridade=Prioridade.ALTA,
        )
        self.client.force_authenticate(user=self.usuario)

    def test_servico_sem_prioridade_no_payload_herda_da_ordem_servico(self):
        url = reverse('servicos-list')
        response = self.client.post(url, {'ordem_servico': self.ordem_servico.pk, 'descricao': 'sem prioridade'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['prioridade'], Prioridade.ALTA)

    def test_servico_com_prioridade_explicita_nao_herda(self):
        url = reverse('servicos-list')
        response = self.client.post(url, {
            'ordem_servico': self.ordem_servico.pk, 'descricao': 'com prioridade', 'prioridade': Prioridade.BAIXA,
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['prioridade'], Prioridade.BAIXA)

    def test_mudar_prioridade_da_os_nao_altera_servico_ja_criado(self):
        servico = Servico.objects.create(
            ordem_servico=self.ordem_servico, descricao='ja criado', prioridade=Prioridade.ALTA,
        )
        self.ordem_servico.prioridade = Prioridade.MEDIA
        self.ordem_servico.save()

        servico.refresh_from_db()
        self.assertEqual(servico.prioridade, Prioridade.ALTA)

    def test_tarefa_sem_prioridade_no_payload_herda_do_servico(self):
        servico = Servico.objects.create(
            ordem_servico=self.ordem_servico, descricao='servico pai', prioridade=Prioridade.ALTA,
        )
        url = reverse('tarefas-list')
        response = self.client.post(url, {
            'servico': servico.pk, 'responsavel': self.usuario.pk, 'descricao': 'sem prioridade',
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['prioridade'], Prioridade.ALTA)


class TarefaFiltrosTestCase(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='tecnico_filtros',
            email='filtros@ergogroup.test',
            password='senha-teste-123',
            nome_completo='Tecnico Filtros',
            tipo_usuario=TipoUsuario.GESTOR_TECNICO,
        )
        self.cliente = Cliente.objects.create(nome='Cliente Filtros')
        self.ordem_servico = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=timezone.localdate(), valor=0,
        )
        self.servico = Servico.objects.create(ordem_servico=self.ordem_servico, descricao='servico')

        hoje = timezone.localdate()
        self.tarefa_atrasada = Tarefa.objects.create(
            servico=self.servico, responsavel=self.usuario, descricao='atrasada',
            prazo=hoje - timedelta(days=2), prioridade=Prioridade.ALTA,
        )
        self.tarefa_futura = Tarefa.objects.create(
            servico=self.servico, responsavel=self.usuario, descricao='futura',
            prazo=hoje + timedelta(days=5), prioridade=Prioridade.BAIXA,
        )
        self.client.force_authenticate(user=self.usuario)

    def test_filtro_prioridade(self):
        url = reverse('tarefas-list')
        response = self.client.get(url, {'prioridade': Prioridade.ALTA})

        ids = {item['id'] for item in response.data}
        self.assertEqual(ids, {self.tarefa_atrasada.pk})

    def test_filtro_atrasada_true(self):
        url = reverse('tarefas-list')
        response = self.client.get(url, {'atrasada': 'true'})

        ids = {item['id'] for item in response.data}
        self.assertEqual(ids, {self.tarefa_atrasada.pk})

    def test_filtro_atrasada_deixa_de_contar_apos_concluir(self):
        self.tarefa_atrasada.status = StatusTarefa.CONCLUIDA
        self.tarefa_atrasada.save()

        url = reverse('tarefas-list')
        response = self.client.get(url, {'atrasada': 'true'})

        self.assertEqual(response.data, [])


class NotificacoesEmailTestCase(APITestCase):
    def setUp(self):
        mail.outbox = []
        self.cliente = Cliente.objects.create(nome='Cliente Notificacoes')

        self.gestor_financeiro = Usuario.objects.create_user(
            username='gestor_financeiro', email='gestor_financeiro@ergogroup.test',
            password='senha-teste-123', nome_completo='Gestor Financeiro',
            tipo_usuario=TipoUsuario.GESTOR_FINANCEIRO,
        )
        self.financeiro = Usuario.objects.create_user(
            username='financeiro', email='financeiro@ergogroup.test',
            password='senha-teste-123', nome_completo='Financeiro',
            tipo_usuario=TipoUsuario.FINANCEIRO,
        )
        self.comercial = Usuario.objects.create_user(
            username='comercial', email='comercial@ergogroup.test',
            password='senha-teste-123', nome_completo='Comercial',
            tipo_usuario=TipoUsuario.COMERCIAL,
        )
        self.tecnico = Usuario.objects.create_user(
            username='tecnico_notif', email='tecnico_notif@ergogroup.test',
            password='senha-teste-123', nome_completo='Tecnico Notif',
            tipo_usuario=TipoUsuario.TECNICO,
        )
        self.outro_tecnico = Usuario.objects.create_user(
            username='outro_tecnico_notif', email='outro_tecnico_notif@ergogroup.test',
            password='senha-teste-123', nome_completo='Outro Tecnico Notif',
            tipo_usuario=TipoUsuario.TECNICO,
        )
        self.administrativo = Usuario.objects.create_user(
            username='administrativo_notif', email='administrativo_notif@ergogroup.test',
            password='senha-teste-123', nome_completo='Administrativo Notif',
            tipo_usuario=TipoUsuario.ADMINISTRATIVO,
        )

    def test_criacao_contrato_segmenta_por_acesso_a_valores(self):
        mail.outbox = []
        with self.captureOnCommitCallbacks(execute=True):
            OrdemServico.objects.create(
                cliente=self.cliente, data_venda=timezone.localdate(), valor=1000,
                contrato=True, objeto_contrato='Objeto', contrato_data_inicio=timezone.localdate(),
                contrato_data_fim=timezone.localdate() + timedelta(days=30),
            )

        self.assertEqual(len(mail.outbox), 2)
        emails_enviados = {to for msg in mail.outbox for to in msg.to}
        self.assertIn(self.tecnico.email, emails_enviados)
        self.assertIn(self.gestor_financeiro.email, emails_enviados)

        msg_sem_valores = next(msg for msg in mail.outbox if self.tecnico.email in msg.to)
        msg_com_valores = next(msg for msg in mail.outbox if self.gestor_financeiro.email in msg.to)
        self.assertNotIn('Dados financeiros', msg_sem_valores.alternatives[0][0])
        self.assertIn('Dados financeiros', msg_com_valores.alternatives[0][0])

    def test_atribuicao_de_tarefa_notifica_responsavel(self):
        ordem_servico = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=timezone.localdate(), valor=0,
        )
        servico = Servico.objects.create(ordem_servico=ordem_servico, descricao='servico')

        mail.outbox = []
        with self.captureOnCommitCallbacks(execute=True):
            tarefa = Tarefa.objects.create(
                servico=servico, responsavel=self.tecnico, descricao='tarefa nova',
            )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.tecnico.email])

        mail.outbox = []
        with self.captureOnCommitCallbacks(execute=True):
            tarefa.responsavel = self.outro_tecnico
            tarefa.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.outro_tecnico.email])

        mail.outbox = []
        with self.captureOnCommitCallbacks(execute=True):
            tarefa.descricao = 'sem trocar responsavel'
            tarefa.save()
        self.assertEqual(len(mail.outbox), 0)

    def test_liberacao_automatica_de_cobranca_notifica_financeiro(self):
        ordem_servico = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=timezone.localdate(), valor=500,
        )
        servico = Servico.objects.create(ordem_servico=ordem_servico, descricao='servico')
        tarefa = Tarefa.objects.create(servico=servico, responsavel=self.tecnico, descricao='tarefa')

        mail.outbox = []
        with self.captureOnCommitCallbacks(execute=True):
            tarefa.status = StatusTarefa.CONCLUIDA
            tarefa.save()

        ordem_servico.refresh_from_db()
        self.assertTrue(ordem_servico.liberada_para_cobranca)

        emails_liberacao = [msg for msg in mail.outbox if 'liberada para cobrança' in msg.subject]
        self.assertEqual(len(emails_liberacao), 1)
        self.assertEqual(set(emails_liberacao[0].to), {self.gestor_financeiro.email, self.financeiro.email})

    def test_cobranca_realizada_na_os_notifica_financeiro_e_comercial(self):
        ordem_servico = OrdemServico.objects.create(
            cliente=self.cliente, data_venda=timezone.localdate(), valor=500,
            liberada_para_cobranca=True,
        )

        mail.outbox = []
        with self.captureOnCommitCallbacks(execute=True):
            ordem_servico.cobranca_realizada = True
            ordem_servico.numero_nf = 123
            ordem_servico.save(update_fields=['cobranca_realizada', 'numero_nf'])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            set(mail.outbox[0].to),
            {self.gestor_financeiro.email, self.financeiro.email, self.comercial.email},
        )

    def test_liberacao_e_cobranca_realizada_na_os_operacional(self):
        catalogo_operacional = CatalogoOperacional.objects.create(nome='Catalogo Operacional Notif')
        oso = OrdemServicoOperacional.objects.create(
            cliente=self.cliente, catalogo_operacional=catalogo_operacional, responsavel=self.tecnico,
            data_recebimento=timezone.localdate(), revisao_cliente=True,
        )

        mail.outbox = []
        with self.captureOnCommitCallbacks(execute=True):
            oso.status = StatusOrdemServicoOperacional.FINALIZADA
            oso.save()

        emails_liberacao = [msg for msg in mail.outbox if 'liberada para cobrança' in msg.subject]
        self.assertEqual(len(emails_liberacao), 1)

        mail.outbox = []
        with self.captureOnCommitCallbacks(execute=True):
            oso.cobranca_realizada = True
            oso.save()

        emails_cobranca = [msg for msg in mail.outbox if 'cobrança realizada' in msg.subject]
        self.assertEqual(len(emails_cobranca), 1)
        self.assertEqual(
            set(emails_cobranca[0].to),
            {self.gestor_financeiro.email, self.financeiro.email, self.comercial.email},
        )
