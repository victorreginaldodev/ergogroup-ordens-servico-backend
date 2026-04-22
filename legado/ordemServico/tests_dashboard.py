from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from legado.ordemServico.models import (
    Cliente,
    MiniOS,
    OrdemServico,
    Profile,
    Repositorio,
    RepositorioMiniOS,
    Servico,
    Tarefa,
)


class AnaliseDadosAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password')
        self.profile = Profile.objects.create(user=self.user, role=1)
        self.client.force_authenticate(user=self.user)

        self.cliente1 = Cliente.objects.create(nome='Cliente 1')
        self.cliente2 = Cliente.objects.create(nome='Cliente 2')

        today = timezone.now().date()

        self.os_concluida = OrdemServico.objects.create(
            cliente=self.cliente1,
            data_criacao=today,
            valor=1000,
            concluida='sim',
            faturamento='sim',
        )
        self.os_pendente = OrdemServico.objects.create(
            cliente=self.cliente2,
            data_criacao=today,
            valor=500,
            concluida='nao',
            faturamento='nao',
        )

        self.repo1 = Repositorio.objects.create(nome='Repo 1')
        self.repo2 = Repositorio.objects.create(nome='Repo 2')
        self.repo_minios = RepositorioMiniOS.objects.create(nome='MiniOS Repo', descricao='Desc')

        recente = today - timedelta(days=30)
        self.recente_data = recente
        antigo = today - timedelta(days=400)

        self.servico1 = Servico.objects.create(
            ordem_servico=self.os_concluida,
            repositorio=self.repo1,
            descricao='Servico 1',
            status='concluida',
            data_conclusao=recente,
        )
        self.servico2 = Servico.objects.create(
            ordem_servico=self.os_concluida,
            repositorio=self.repo1,
            descricao='Servico 2',
            status='concluida',
            data_conclusao=recente,
        )
        self.servico_antigo = Servico.objects.create(
            ordem_servico=self.os_concluida,
            repositorio=self.repo2,
            descricao='Servico antigo',
            status='concluida',
            data_conclusao=antigo,
        )
        self.servico_pendente = Servico.objects.create(
            ordem_servico=self.os_pendente,
            repositorio=self.repo2,
            descricao='Servico pendente',
            status='em_andamento',
        )

        self.profile_tecnico = Profile.objects.create(
            user=User.objects.create_user(username='tech', password='pwd'),
            role=5,
        )

        tarefa1 = Tarefa.objects.create(
            ordem_servico=self.os_pendente,
            servico=self.servico_pendente,
            profile=self.profile,
            status='concluida',
            data_termino=self.recente_data,
        )
        tarefa2 = Tarefa.objects.create(
            ordem_servico=self.os_pendente,
            servico=self.servico_pendente,
            profile=self.profile_tecnico,
            status='em_andamento',
        )
        tarefa_antiga = Tarefa.objects.create(
            ordem_servico=self.os_pendente,
            servico=self.servico_pendente,
            profile=self.profile,
            status='nao_iniciada',
        )
        Tarefa.objects.filter(pk=tarefa_antiga.pk).update(
            updated_at=timezone.now() - timedelta(days=400)
        )

        Servico.objects.filter(pk__in=[self.servico1.pk, self.servico2.pk]).update(
            status='concluida',
            data_conclusao=self.recente_data,
        )
        self.servico1.refresh_from_db()
        self.servico2.refresh_from_db()

        self.os_concluida.refresh_from_db()
        self.os_concluida.concluida = 'sim'
        self.os_concluida.save(update_fields=['concluida'])

        self.minios_finalizada = MiniOS.objects.create(
            cliente=self.cliente1,
            servico=self.repo_minios,
            profile=self.profile,
            status='finalizada',
            data_termino=self.recente_data,
        )
        self.minios_antiga = MiniOS.objects.create(
            cliente=self.cliente1,
            servico=self.repo_minios,
            profile=self.profile,
            status='finalizada',
            data_termino=antigo,
        )
        self.minios_pendente = MiniOS.objects.create(
            cliente=self.cliente2,
            servico=self.repo_minios,
            profile=self.profile_tecnico,
            status='em_andamento',
        )

    def test_dashboard_analise_dados(self):
        url = reverse('analise-dados')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        ordens = data['ordens_servico']
        self.assertEqual(ordens['total'], 2)
        self.assertEqual(ordens['total_concluidas'], 1)
        self.assertEqual(ordens['total_nao_concluidas'], 1)

        servicos = data['servicos']
        self.assertEqual(servicos['concluidos_ultimos_12_meses_total'], 2)

        concluidos_mes = servicos['concluidos_por_mes']
        self.assertEqual(len(concluidos_mes), 12)
        alvo_mes = next(
            item for item in concluidos_mes if item['ano'] == self.recente_data.year and item['mes'] == self.recente_data.month
        )
        self.assertEqual(alvo_mes['total'], 2)


        principais = servicos['principais_por_quantidade']
        self.assertTrue(any(item['repositorio_nome'] == 'Repo 1' and item['total'] == 2 for item in principais))

        servicos_status = {item['status']: item['total'] for item in servicos['por_status']}
        self.assertEqual(servicos_status.get('concluida'), 2)
        self.assertEqual(servicos_status.get('em_andamento'), 2)

        tarefas = data['tarefas']
        tarefas_status = {item['status']: item['total'] for item in tarefas['por_status']}
        self.assertEqual(tarefas_status.get('concluida'), 1)
        self.assertEqual(tarefas_status.get('em_andamento'), 1)
        self.assertEqual(tarefas_status.get('nao_iniciada'), 1)

        tarefas_concluidas_mes = tarefas['concluidas_por_mes']
        self.assertEqual(len(tarefas_concluidas_mes), 12)
        alvo_tarefa_mes = next(
            item for item in tarefas_concluidas_mes
            if item['ano'] == self.recente_data.year and item['mes'] == self.recente_data.month
        )
        self.assertEqual(alvo_tarefa_mes['total'], 1)

        minios_data = data['minios']
        self.assertEqual(minios_data['concluidas_ultimos_12_meses_total'], 1)
        minios_por_mes = minios_data['concluidas_por_mes']
        self.assertEqual(len(minios_por_mes), 12)
        alvo_minios_mes = next(
            item for item in minios_por_mes
            if item['ano'] == self.recente_data.year and item['mes'] == self.recente_data.month
        )
        self.assertEqual(alvo_minios_mes['total'], 1)

        clientes = data['clientes']['mais_faturamento']
        self.assertTrue(any(item['cliente_nome'] == 'Cliente 1' and item['total_valor_faturado'] == 1000 for item in clientes))

