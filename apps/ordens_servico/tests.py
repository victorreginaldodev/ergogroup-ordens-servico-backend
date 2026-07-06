from datetime import timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.clientes.models import Cliente
from apps.contas.models import Usuario
from apps.contas.models.choices import TipoUsuario
from apps.catalogo.models import Catalogo, Complexidade
from apps.ordens_servico.models import OrdemServico, Servico, Tarefa, Prioridade
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
