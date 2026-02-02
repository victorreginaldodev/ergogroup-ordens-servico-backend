from django.test import TestCase
from django.contrib.auth.models import User
from ordemServico.models import MiniOS, Cliente, Profile, RepositorioMiniOS
from ordemServico.api.AnaliseDadosAPIView import AnaliseDadosAPIView
from rest_framework.test import APIRequestFactory, force_authenticate

class AnaliseDadosMiniOSTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = Profile.objects.create(user=self.user)
        self.cliente = Cliente.objects.create(nome="Cliente Teste")
        self.servico = RepositorioMiniOS.objects.create(nome="Servico Teste")
        self.servico_correcao = RepositorioMiniOS.objects.create(nome="Correção Cliente")
        self.factory = APIRequestFactory()
        self.view = AnaliseDadosAPIView.as_view()

    def test_minios_totals(self):
        # Create MiniOS instances
        # 1. Standard MiniOS
        MiniOS.objects.create(
            cliente=self.cliente,
            servico=self.servico,
            profile=self.profile,
            status='nao_iniciado',
            revisao_cliente=False
        )
        
        # 2. MiniOS with revisao_cliente=True (Explicitly set or by signal if it works)
        # Note: We rely on explicit setting here to test the API view logic, 
        # though the save signal we added earlier should also work.
        MiniOS.objects.create(
            cliente=self.cliente,
            servico=self.servico_correcao,
            profile=self.profile,
            status='nao_iniciado',
            revisao_cliente=True
        )
        
        # 3. Another one with revisao_cliente=True
        MiniOS.objects.create(
            cliente=self.cliente,
            servico=self.servico_correcao,
            profile=self.profile,
            status='finalizada',
            revisao_cliente=True
        )

        request = self.factory.get('/api/analise-dados/')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        self.assertIn('minios', data)
        minios_data = data['minios']
        
        self.assertIn('total', minios_data)
        self.assertIn('total_revisao_cliente', minios_data)
        
        # Check totals
        self.assertEqual(minios_data['total'], 3)
        self.assertEqual(minios_data['total_revisao_cliente'], 2)
