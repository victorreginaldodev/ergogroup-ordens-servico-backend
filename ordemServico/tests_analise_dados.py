from django.test import TestCase
from django.contrib.auth.models import User
from ordemServico.models import OrdemServico, Cliente, Profile
from ordemServico.api.AnaliseDadosAPIView import AnaliseDadosAPIView
from rest_framework.test import APIRequestFactory, force_authenticate
from django.utils import timezone
from datetime import timedelta, date

class AnaliseDadosAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = Profile.objects.create(user=self.user)
        self.factory = APIRequestFactory()
        self.view = AnaliseDadosAPIView.as_view()

    def test_analise_dados(self):
        # Create Clients
        c1 = Cliente.objects.create(nome="Cliente 1")
        c2 = Cliente.objects.create(nome="Cliente 2")
        c3 = Cliente.objects.create(nome="Cliente 3")
        
        today = timezone.now().date()
        
        # OS for c1 (Total 300)
        OrdemServico.objects.create(cliente=c1, data_criacao=today, valor=100.0)
        OrdemServico.objects.create(cliente=c1, data_criacao=today, valor=200.0)
        
        # OS for c2 (Total 500)
        OrdemServico.objects.create(cliente=c2, data_criacao=today, valor=500.0)
        
        # OS for c3 (Total 50)
        OrdemServico.objects.create(cliente=c3, data_criacao=today, valor=50.0)
        
        request = self.factory.get('/api/analise-dados/')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        # Check vendas_por_mes
        vendas = data['ordens_servico']['vendas_por_mes']
        self.assertEqual(len(vendas), 12)
        current_month = next((item for item in vendas if item['mes'] == today.month), None)
        self.assertEqual(current_month['total'], 850.0) # 300+500+50
        
        # Check clientes mais vendas
        clientes_vendas = data['clientes']['mais_vendas']
        self.assertTrue(len(clientes_vendas) >= 3)
        
        # First should be c2 (500)
        self.assertEqual(clientes_vendas[0]['cliente_nome'], "Cliente 2")
        self.assertEqual(clientes_vendas[0]['total_valor_vendas'], 500.0)
        
        # Second should be c1 (300)
        self.assertEqual(clientes_vendas[1]['cliente_nome'], "Cliente 1")
        self.assertEqual(clientes_vendas[1]['total_valor_vendas'], 300.0)
        
        # Third should be c3 (50)
        self.assertEqual(clientes_vendas[2]['cliente_nome'], "Cliente 3")
        self.assertEqual(clientes_vendas[2]['total_valor_vendas'], 50.0)
