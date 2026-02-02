from django.test import TestCase
from django.contrib.auth.models import User
from ordemServico.models import Servico, Cliente, Profile, Repositorio, OrdemServico
from ordemServico.serializers.ServicoSerializer import ServicoListSerializer
from django.utils import timezone
from datetime import date

class ServicoListSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.cliente = Cliente.objects.create(nome="Cliente Teste")
        self.os = OrdemServico.objects.create(
            cliente=self.cliente,
            data_criacao=date(2023, 10, 1),
            valor=100.0
        )
        self.repositorio = Repositorio.objects.create(nome="Repo Teste")
        self.servico = Servico.objects.create(
            ordem_servico=self.os,
            repositorio=self.repositorio,
            status='nao_iniciado'
        )

    def test_data_criacao_field(self):
        serializer = ServicoListSerializer(instance=self.servico)
        data = serializer.data
        
        self.assertIn('data_criacao', data)
        self.assertEqual(data['data_criacao'], '2023-10-01')
