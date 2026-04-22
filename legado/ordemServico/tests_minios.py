from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from legado.ordemServico.models import MiniOS, Cliente, RepositorioMiniOS, Profile, Tarefa
from legado.ordemServico.api.MiniOSViewSet import MiniOSViewSet
from legado.ordemServico.views.TarefaMiniOSAPIView import TarefaMiniOSAPIView
from django.utils import timezone
from rest_framework.test import force_authenticate
import json

class MiniOSTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = Profile.objects.create(user=self.user)
        self.cliente = Cliente.objects.create(nome="Cliente MiniOS")
        self.repo_minios = RepositorioMiniOS.objects.create(nome="Repo MiniOS", descricao="Desc")
        
        self.minios = MiniOS.objects.create(
            cliente=self.cliente,
            servico=self.repo_minios,
            profile=self.profile,
            status='nao_iniciado',
            data_inicio=timezone.now().date()
        )
        self.factory = RequestFactory()

    def test_minios_crud(self):
        # List
        request = self.factory.get('/api/minios/')
        force_authenticate(request, user=self.user)
        view = MiniOSViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.minios.id)

        # Retrieve
        request = self.factory.get(f'/api/minios/{self.minios.id}/')
        force_authenticate(request, user=self.user)
        view = MiniOSViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=self.minios.id)
        self.assertEqual(response.status_code, 200)
        # Check nested representation (assuming to_representation works)
        # If to_representation converts to dict, access by key
        self.assertEqual(response.data['cliente']['nome'], "Cliente MiniOS")

        # Create
        data = {
            'cliente': self.cliente.id,
            'servico': self.repo_minios.id,
            'profile': self.profile.id,
            'status': 'nao_iniciado',
            'quantidade': 2
        }
        request = self.factory.post('/api/minios/', data)
        force_authenticate(request, user=self.user)
        view = MiniOSViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(MiniOS.objects.count(), 2)

        # Update
        new_status = 'em_andamento'
        data_update = {'status': new_status}
        request = self.factory.patch(
            f'/api/minios/{self.minios.id}/', 
            data=json.dumps(data_update), 
            content_type='application/json'
        )
        force_authenticate(request, user=self.user)
        view = MiniOSViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=self.minios.id)
        self.assertEqual(response.status_code, 200)
        self.minios.refresh_from_db()
        self.assertEqual(self.minios.status, new_status)

        # Delete
        request = self.factory.delete(f'/api/minios/{self.minios.id}/')
        force_authenticate(request, user=self.user)
        view = MiniOSViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.minios.id)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(MiniOS.objects.count(), 1)

    def test_tarefa_minios_list_has_id(self):
        request = self.factory.get('/api/tarefas-minios/')
        force_authenticate(request, user=self.user)
        view = TarefaMiniOSAPIView.as_view()
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        found_minios = False
        for item in data:
            if item.get('type') == 'minios':
                found_minios = True
                self.assertIn('id', item)
                self.assertEqual(item['id'], self.minios.id)
        
        self.assertTrue(found_minios)

    def test_minios_tecnico_filter(self):
        # Set current user as technician (role 5)
        self.profile.role = 5
        self.profile.save()

        # Create another user (technician)
        user2 = User.objects.create_user(username='tech2', password='password')
        profile2 = Profile.objects.create(user=user2, role=5)
        
        # Create minios for user2
        minios2 = MiniOS.objects.create(
            cliente=self.cliente,
            servico=self.repo_minios,
            profile=profile2,
            status='nao_iniciado',
            data_inicio=timezone.now().date()
        )

        # Test MiniOSViewSet list
        request = self.factory.get('/api/minios/')
        force_authenticate(request, user=self.user)
        view = MiniOSViewSet.as_view({'get': 'list'})
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        # Should only see own minios (self.minios)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.minios.id)

        # Test TarefaMiniOSAPIView list
        request = self.factory.get('/api/tarefas-minios/')
        force_authenticate(request, user=self.user)
        view = TarefaMiniOSAPIView.as_view()
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        # Filter for minios type
        minios_list = [item for item in data if item.get('type') == 'minios']
        
        # Should only see own minios
        self.assertEqual(len(minios_list), 1)
        self.assertEqual(minios_list[0]['id'], self.minios.id)

    def test_minios_admin_sees_all(self):
        # Set current user as Director (role 1)
        self.profile.role = 1
        self.profile.save()

        # Create another user (technician)
        user2 = User.objects.create_user(username='tech2', password='password')
        profile2 = Profile.objects.create(user=user2, role=5)
        
        # Create minios for user2
        minios2 = MiniOS.objects.create(
            cliente=self.cliente,
            servico=self.repo_minios,
            profile=profile2,
            status='nao_iniciado',
            data_inicio=timezone.now().date()
        )

        # Test MiniOSViewSet list
        request = self.factory.get('/api/minios/')
        force_authenticate(request, user=self.user)
        view = MiniOSViewSet.as_view({'get': 'list'})
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        # Should see all minios (self.minios + minios2)
        self.assertEqual(len(response.data), 2)

    def test_os_rapidas_endpoint_filters_and_requires_permission(self):
        # Technician (default) should not access
        request = self.factory.get('/api/minios/os-rapidas/')
        force_authenticate(request, user=self.user)
        view = MiniOSViewSet.as_view({'get': 'os_rapidas'})
        response = view(request)
        self.assertEqual(response.status_code, 403)

        # Promote user to administrativo and create matching MiniOS
        self.profile.role = 2
        self.profile.save()
        repo_correcao = RepositorioMiniOS.objects.create(
            nome="Correção Cliente ABC",
            descricao="Servico de correção",
        )
        os_rapida = MiniOS.objects.create(
            cliente=self.cliente,
            servico=repo_correcao,
            profile=self.profile,
            status='nao_iniciado',
        )

        request = self.factory.get('/api/minios/os-rapidas/')
        force_authenticate(request, user=self.user)
        view = MiniOSViewSet.as_view({'get': 'os_rapidas'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], os_rapida.id)
        self.assertEqual(response.data[0]['servico']['nome'], repo_correcao.nome)

    def test_os_rapidas_faturar_action_updates_fields(self):
        self.profile.role = 1
        self.profile.save()
        repo_correcao = RepositorioMiniOS.objects.create(
            nome="CORREÇÃO CLIENTE XPTO",
            descricao="Servico de correção",
        )
        os_rapida = MiniOS.objects.create(
            cliente=self.cliente,
            servico=repo_correcao,
            profile=self.profile,
            faturamento='nao',
            n_nf='',
        )

        data_update = {'faturamento': 'sim', 'n_nf': '12345'}
        request = self.factory.patch(
            f'/api/minios/{os_rapida.id}/faturar/',
            data=json.dumps(data_update),
            content_type='application/json',
        )
        force_authenticate(request, user=self.user)
        view = MiniOSViewSet.as_view({'patch': 'faturar'})
        response = view(request, pk=os_rapida.id)

        self.assertEqual(response.status_code, 200)
        os_rapida.refresh_from_db()
        self.assertEqual(os_rapida.faturamento, 'sim')
        self.assertEqual(os_rapida.n_nf, '12345')
