from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from ordemServico.models import OrdemServico, Cliente, Servico, Repositorio, Profile, Tarefa
from ordemServico.serializers.OrdemServicoSerializer import OrdemServicoSerializer
from ordemServico.api.OrdemServicoViewSet import OrdemServicoViewSet
from ordemServico.api.ServicoViewSet import ServicoViewSet
from ordemServico.api.TarefaViewSet import TarefaViewSet
from ordemServico.api.FinanceiroKPIsAPIView import FinanceiroKPIsAPIView
from django.utils import timezone
from rest_framework.test import force_authenticate, APIRequestFactory

class OrdemServicoSerializerUpdateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = Profile.objects.create(user=self.user)
        self.cliente = Cliente.objects.create(nome="Cliente Teste")
        self.os = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            valor=100.0,
            concluida='nao',
            faturamento='nao'
        )
        self.repositorio = Repositorio.objects.create(nome="Repo 1")
        self.servico1 = Servico.objects.create(
            ordem_servico=self.os,
            repositorio=self.repositorio,
            descricao="Servico 1"
        )
        self.servico2 = Servico.objects.create(
            ordem_servico=self.os,
            repositorio=self.repositorio,
            descricao="Servico 2"
        )
        self.tarefa = Tarefa.objects.create(
            servico=self.servico1,
            profile=self.profile,
            status='nao_iniciada'
        )
        self.factory = RequestFactory()
        self.api_factory = APIRequestFactory()

    def test_update_os_with_nested_servicos(self):
        # We simulate the payload.
        # Note: In a real request, IDs might be strings or ints.
        
        data = {
            'cliente': self.cliente.id,
            'valor': 200.0,
            'servicos': [
                {
                    'id': self.servico1.id,
                    'repositorio_id': self.repositorio.id,
                    'descricao': "Servico 1 Updated"
                },
                {
                    # New service
                    'repositorio_id': self.repositorio.id,
                    'descricao': "Servico 3 New"
                }
            ]
        }
        
        # When passing data to serializer, if we use partial=True, we can omit fields.
        serializer = OrdemServicoSerializer(instance=self.os, data=data, partial=True)
        
        # We need to simulate the context where 'servicos' is in initial_data
        # ModelSerializer does this automatically.
        
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_os = serializer.save()
        
        self.os.refresh_from_db()
        self.assertEqual(self.os.valor, 200.0)
        
        # Check services
        self.assertEqual(self.os.servicos.count(), 2)
        
        # Check Servico 1 updated
        s1 = self.os.servicos.filter(id=self.servico1.id).first()
        self.assertIsNotNone(s1)
        self.assertEqual(s1.descricao, "Servico 1 Updated")
        
        # Check Servico 2 deleted
        self.assertFalse(self.os.servicos.filter(id=self.servico2.id).exists())
        
        # Check Servico 3 created
        s3 = self.os.servicos.exclude(id=self.servico1.id).first()
        self.assertIsNotNone(s3)
        self.assertEqual(s3.descricao, "Servico 3 New")

    def test_list_servico_fields(self):
        request = self.factory.get('/api/servico/')
        force_authenticate(request, user=self.user)
        view = ServicoViewSet.as_view({'get': 'list'})
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        
        # Expected fields: 'id', 'ordem_servico', 'cliente_nome', 'repositorio', 'status', 'tem_tarefas'
        expected_fields = {'id', 'ordem_servico', 'cliente_nome', 'repositorio', 'status', 'tem_tarefas'}
        
        # Check first item keys
        item = response.data[0]
        self.assertEqual(set(item.keys()), expected_fields)
        
        # Verify values for specific services
        item_s1 = next((i for i in response.data if i['id'] == self.servico1.id), None)
        item_s2 = next((i for i in response.data if i['id'] == self.servico2.id), None)
        
        self.assertIsNotNone(item_s1)
        self.assertEqual(item_s1['cliente_nome'], "Cliente Teste")
        self.assertEqual(item_s1['repositorio']['nome'], "Repo 1")
        self.assertTrue(item_s1['tem_tarefas']) # servico1 has task created in setUp

        self.assertIsNotNone(item_s2)
        self.assertFalse(item_s2['tem_tarefas']) # servico2 has no tasks

    def test_list_tarefa_tecnico_filter(self):
        # Create another tech and task
        user2 = User.objects.create_user(username='tech2', password='password')
        profile2 = Profile.objects.create(user=user2, role=5)
        tarefa2 = Tarefa.objects.create(
            servico=self.servico1,
            profile=profile2,
            status='nao_iniciada'
        )
        
        # Test TarefaViewSet list
        from ordemServico.api.TarefaViewSet import TarefaViewSet
        request = self.factory.get('/api/tarefa/')
        force_authenticate(request, user=self.user)
        view = TarefaViewSet.as_view({'get': 'list'})
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        # Should only see own task (self.tarefa)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.tarefa.id)

    def test_list_tarefa_admin_sees_all(self):
        # Create admin user
        admin_user = User.objects.create_user(username='admin', password='password')
        Profile.objects.create(user=admin_user, role=1) # 1 = Diretor
        
        # Create another tech and task
        user2 = User.objects.create_user(username='tech2', password='password')
        profile2 = Profile.objects.create(user=user2, role=5)
        tarefa2 = Tarefa.objects.create(
            servico=self.servico1,
            profile=profile2,
            status='nao_iniciada'
        )

        from ordemServico.api.TarefaViewSet import TarefaViewSet
        request = self.factory.get('/api/tarefa/')
        force_authenticate(request, user=admin_user)
        view = TarefaViewSet.as_view({'get': 'list'})
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        # Should see all tasks (self.tarefa + tarefa2)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_tarefa_detail_structure(self):
        # Setup data for detail test
        self.cliente.nome_representante = "Rep Detail"
        self.cliente.setor_representante = "Setor Detail"
        self.cliente.email_representante = "rep@detail.com"
        self.cliente.contato_representante = "999999999"
        self.cliente.save()
        
        self.tarefa.descricao = "Descricao Tarefa Teste"
        self.tarefa.data_inicio = timezone.now().date()
        self.tarefa.data_termino = timezone.now().date() + timezone.timedelta(days=2)
        self.tarefa.save()
        
        from ordemServico.api.TarefaViewSet import TarefaViewSet
        request = self.factory.get(f'/api/tarefa/{self.tarefa.id}/')
        force_authenticate(request, user=self.user)
        view = TarefaViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=self.tarefa.id)
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        # Verify structure
        self.assertIn('cliente', data)
        self.assertIn('servico_info', data)
        self.assertIn('descricao', data)
        self.assertIn('data_inicio', data)
        self.assertIn('data_termino', data)
        self.assertIn('status', data)
        
        # Verify Cliente fields
        cliente = data['cliente']
        self.assertEqual(cliente['nome'], "Cliente Teste")
        self.assertEqual(cliente['representante']['nome'], "Rep Detail")
        self.assertEqual(cliente['representante']['setor'], "Setor Detail")
        self.assertEqual(cliente['representante']['email'], "rep@detail.com")
        self.assertEqual(cliente['contato'], "999999999")
        
        # Verify Servico fields
        servico = data['servico_info']
        self.assertEqual(servico['descricao'], "Servico 1")
        self.assertEqual(servico['nome_repositorio'], "Repo 1")
        self.assertEqual(servico['status'], "em_espera")
        
        # Verify Tarefa fields
        self.assertEqual(data['descricao'], "Descricao Tarefa Teste")
        self.assertEqual(data['status'], "nao_iniciada")

    def test_retrieve_servico_detail_fields(self):
        # Update client info
        self.cliente.nome_representante = "Rep Name"
        self.cliente.setor_representante = "IT"
        self.cliente.email_representante = "rep@test.com"
        self.cliente.contato_representante = "123456789"
        self.cliente.save()

        request = self.factory.get(f'/api/servico/{self.servico1.id}/')
        force_authenticate(request, user=self.user)
        view = ServicoViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=self.servico1.id)
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        # Check Ordem Servico Detail
        self.assertIn('ordem_servico_detail', data)
        os_detail = data['ordem_servico_detail']
        self.assertEqual(os_detail['id'], self.os.id)
        self.assertEqual(os_detail['valor'], 100.0)
        self.assertEqual(os_detail['concluida'], 'nao')
        
        # Check Client Detail nested in OS
        self.assertIn('cliente', os_detail)
        client_detail = os_detail['cliente']
        self.assertEqual(client_detail['nome'], "Cliente Teste")
        self.assertEqual(client_detail['nome_representante'], "Rep Name")
        self.assertEqual(client_detail['email_representante'], "rep@test.com")

        # Check Tarefas ID
        self.assertIn('tarefas', data)
        self.assertTrue(len(data['tarefas']) > 0)
        tarefa_item = data['tarefas'][0]
        self.assertIn('id', tarefa_item)
        self.assertEqual(tarefa_item['id'], self.tarefa.id)
        self.assertIn('descricao', tarefa_item)

    def test_list_tarefa_fields(self):
        # Update tarefa description
        self.tarefa.descricao = "Tarefa Descricao Teste"
        self.tarefa.save()

        request = self.factory.get('/api/tarefa/')
        force_authenticate(request, user=self.user)
        view = TarefaViewSet.as_view({'get': 'list'})
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        item = response.data[0]
        
        # Expected fields: 'id', 'cliente_nome', 'repositorio_nome', 'usuario_nome', 'status', 'descricao', 'servico_descricao'
        expected_fields = {'id', 'cliente_nome', 'repositorio_nome', 'usuario_nome', 'status', 'descricao', 'servico_descricao'}
        self.assertEqual(set(item.keys()), expected_fields)
        self.assertEqual(item['cliente_nome'], "Cliente Teste")
        self.assertEqual(item['repositorio_nome'], "Repo 1")
        self.assertEqual(item['usuario_nome'], "testuser")
        self.assertEqual(item['descricao'], "Tarefa Descricao Teste")
        self.assertEqual(item['servico_descricao'], "Servico 1")

    def test_patch_atualiza_campos_faturamento(self):
        view = OrdemServicoViewSet.as_view({'patch': 'partial_update'})
        data = {
            'faturamento': 'sim',
            'numero_nf': 987,
            'data_faturamento': timezone.now().date().isoformat(),
            'nome_contato_envio_nf': 'Responsável Financeiro',
            'contato_envio_nf': 'financeiro@example.com',
            'observacao': 'Atualização via API',
            'forma_pagamento': 'credito',
            'quantidade_parcelas': 3,
            'cobranca_imediata': 'nao',
        }
        request = self.api_factory.patch(f'/api/ordens-servico/{self.os.id}/', data, format='json')
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.os.id)

        self.assertEqual(response.status_code, 200)

        self.os.refresh_from_db()
        self.assertEqual(self.os.faturamento, 'sim')
        self.assertEqual(self.os.numero_nf, 987)
        self.assertEqual(self.os.data_faturamento.isoformat(), data['data_faturamento'])
        self.assertEqual(self.os.nome_contato_envio_nf, 'Responsável Financeiro')
        self.assertEqual(self.os.contato_envio_nf, 'financeiro@example.com')
        self.assertEqual(self.os.observacao, 'Atualização via API')
        self.assertEqual(self.os.forma_pagamento, 'credito')
        self.assertEqual(self.os.quantidade_parcelas, 3)


class ServicoOrdemConclusaoTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='workflow', password='password')
        self.profile = Profile.objects.create(user=self.user)
        self.cliente = Cliente.objects.create(nome="Cliente Fluxo")
        self.repositorio = Repositorio.objects.create(nome="Repo Fluxo")
        self.ordem = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            concluida='nao',
            faturamento='nao'
        )
        self.servico1 = Servico.objects.create(
            ordem_servico=self.ordem,
            repositorio=self.repositorio,
            descricao="Servico 1"
        )
        self.servico2 = Servico.objects.create(
            ordem_servico=self.ordem,
            repositorio=self.repositorio,
            descricao="Servico 2"
        )

    def test_ordem_so_conclui_quando_todos_servicos_concluidos(self):
        tarefa1 = Tarefa.objects.create(
            servico=self.servico1,
            profile=self.profile,
            status='em_andamento'
        )
        tarefa2 = Tarefa.objects.create(
            servico=self.servico1,
            profile=self.profile,
            status='em_andamento'
        )

        self.servico1.refresh_from_db()
        self.ordem.refresh_from_db()

        self.assertNotEqual(self.servico1.status, 'concluida')
        self.assertIsNone(self.servico1.data_conclusao)
        self.assertEqual(self.ordem.concluida, 'nao')

        tarefa1.status = 'concluida'
        tarefa1.save()

        tarefa2.status = 'concluida'
        tarefa2.save()

        self.servico1.refresh_from_db()
        self.ordem.refresh_from_db()

        self.assertEqual(self.servico1.status, 'concluida')
        self.assertIsNotNone(self.servico1.data_conclusao)
        self.assertEqual(self.ordem.concluida, 'nao')

        Tarefa.objects.create(
            servico=self.servico2,
            profile=self.profile,
            status='concluida'
        )

        self.servico2.refresh_from_db()
        self.ordem.refresh_from_db()

        self.assertEqual(self.servico2.status, 'concluida')
        self.assertEqual(self.ordem.concluida, 'sim')

    def test_reabertura_de_tarefa_reabre_servico_e_ordem(self):
        tarefa1 = Tarefa.objects.create(
            servico=self.servico1,
            profile=self.profile,
            status='concluida'
        )
        tarefa2 = Tarefa.objects.create(
            servico=self.servico2,
            profile=self.profile,
            status='concluida'
        )

        self.servico1.refresh_from_db()
        self.servico2.refresh_from_db()
        self.ordem.refresh_from_db()

        self.assertEqual(self.servico1.status, 'concluida')
        self.assertEqual(self.servico2.status, 'concluida')
        self.assertEqual(self.ordem.concluida, 'sim')

        tarefa1.status = 'em_andamento'
        tarefa1.save()

        self.servico1.refresh_from_db()
        self.servico2.refresh_from_db()
        self.ordem.refresh_from_db()

        self.assertEqual(self.servico1.status, 'em_andamento')
        self.assertIsNone(self.servico1.data_conclusao)
        self.assertEqual(self.servico2.status, 'concluida')
        self.assertEqual(self.ordem.concluida, 'nao')


class OrdemServicoFaturamentoEndpointTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='faturamento', password='password')
        self.profile = Profile.objects.create(user=self.user)
        self.factory = APIRequestFactory()

        self.cliente = Cliente.objects.create(nome="Cliente Faturamento")
        self.repositorio = Repositorio.objects.create(nome="Repo Faturamento")

        self.ordem_concluida = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            concluida='sim',
            cobranca_imediata='nao',
            faturamento='nao'
        )
        Servico.objects.create(
            ordem_servico=self.ordem_concluida,
            repositorio=self.repositorio,
            descricao="Servico concluido",
            status='concluida'
        )

        self.ordem_cobranca_imediata = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            concluida='nao',
            cobranca_imediata='sim',
            faturamento='nao'
        )

        self.ordem_regular = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            concluida='nao',
            cobranca_imediata='nao',
            faturamento='nao'
        )
        Servico.objects.create(
            ordem_servico=self.ordem_regular,
            repositorio=self.repositorio,
            descricao="Servico em andamento",
            status='em_andamento'
        )

        self.ordem_concluida_e_cobranca = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            concluida='sim',
            cobranca_imediata='sim',
            faturamento='nao'
        )
        Servico.objects.create(
            ordem_servico=self.ordem_concluida_e_cobranca,
            repositorio=self.repositorio,
            descricao="Servico concluido cobranca",
            status='concluida'
        )

        self.ordem_faturada = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            concluida='sim',
            cobranca_imediata='sim',
            faturamento='sim'
        )
        Servico.objects.create(
            ordem_servico=self.ordem_faturada,
            repositorio=self.repositorio,
            descricao="Servico faturado",
            status='concluida'
        )

    def test_retorna_ordens_para_faturamento(self):
        view = OrdemServicoViewSet.as_view({'get': 'faturamento'})
        request = self.factory.get('/api/ordens-servico/faturamento/')
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, 200)
        ids = {item['id'] for item in response.data}

        self.assertIn(self.ordem_concluida.id, ids)
        self.assertNotIn(self.ordem_cobranca_imediata.id, ids)
        self.assertIn(self.ordem_concluida_e_cobranca.id, ids)
        self.assertNotIn(self.ordem_regular.id, ids)
        self.assertNotIn(self.ordem_faturada.id, ids)

        item = next(entry for entry in response.data if entry['id'] == self.ordem_concluida.id)
        expected_fields = {
            'id',
            'numero_os',
            'cliente_nome',
            'valor',
            'forma_pagamento',
            'quantidade_parcelas',
            'cobranca_imediata',
            'faturamento_1',
            'nome_contato_envio_nf',
            'contato_envio_nf',
            'observacao',
            'faturamento',
            'data_faturamento',
            'numero_nf',
            'concluida',
        }
        self.assertEqual(set(item.keys()), expected_fields)
        self.assertEqual(item['cliente_nome'], "Cliente Faturamento")
        self.assertEqual(item['numero_os'], self.ordem_concluida.id)
        self.assertEqual(item['forma_pagamento'], 'boleto')
        self.assertEqual(item['cobranca_imediata'], 'nao')
        self.assertEqual(item['concluida'], 'sim')

    def test_nao_duplicar_ordem_que_atende_ambos_criterios(self):
        view = OrdemServicoViewSet.as_view({'get': 'faturamento'})
        request = self.factory.get('/api/ordens-servico/faturamento/')
        force_authenticate(request, user=self.user)
        response = view(request)

        ids = [item['id'] for item in response.data if item['id'] == self.ordem_concluida_e_cobranca.id]
        self.assertEqual(len(ids), 1)


class FinanceiroKPIsAPIViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='financeiro', password='password')
        self.factory = APIRequestFactory()
        self.cliente = Cliente.objects.create(nome="Cliente KPI")
        self.repositorio = Repositorio.objects.create(nome="Repo KPI")

        self.os_faturada = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            valor=100.0,
            concluida='sim',
            faturamento='sim',
            cobranca_imediata='nao'
        )
        Servico.objects.create(
            ordem_servico=self.os_faturada,
            repositorio=self.repositorio,
            descricao="Servico faturado",
            status='concluida'
        )

        self.os_concluida = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            valor=200.0,
            concluida='sim',
            faturamento='nao',
            cobranca_imediata='nao'
        )
        Servico.objects.create(
            ordem_servico=self.os_concluida,
            repositorio=self.repositorio,
            descricao="Servico concluido",
            status='concluida'
        )

        self.os_cobranca_imediata = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            valor=150.0,
            concluida='nao',
            faturamento='nao',
            cobranca_imediata='sim'
        )

        self.os_concluida_e_cobranca = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            valor=80.0,
            concluida='sim',
            faturamento='nao',
            cobranca_imediata='sim'
        )
        Servico.objects.create(
            ordem_servico=self.os_concluida_e_cobranca,
            repositorio=self.repositorio,
            descricao="Servico concluido cobranca",
            status='concluida'
        )

        self.os_sem_liberacao = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=timezone.now().date(),
            valor=60.0,
            concluida='nao',
            faturamento='nao',
            cobranca_imediata='nao'
        )
        Servico.objects.create(
            ordem_servico=self.os_sem_liberacao,
            repositorio=self.repositorio,
            descricao="Servico pendente",
            status='em_andamento'
        )

    def test_retorna_kpis_financeiras(self):
        view = FinanceiroKPIsAPIView.as_view()
        request = self.factory.get('/api/financeiro/kpis/')
        force_authenticate(request, user=self.user)
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_faturado'], 100.0)
        self.assertEqual(response.data['total_para_faturar'], 280.0)
        self.assertEqual(response.data['total_sem_liberacao'], 60.0)
