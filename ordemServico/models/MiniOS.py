from django.db import models
from .Cliente import Cliente
from .Profile import Profile
from .RepositorioMiniOS import RepositorioMiniOS

class MiniOS(models.Model):
    STATUS = (
        ('nao_iniciado', 'NÃO INICIADO'),
        ('em_andamento', 'EM ANDAMENTO'),
        ('finalizada', 'FINALIZADA'),
    )

    FATURAMENTO = (
        ('sim', 'SIM'),
        ('nao', 'NÃO')
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cliente_minios')
    servico = models.ForeignKey(RepositorioMiniOS, on_delete=models.PROTECT, related_name='servico_minios')
    quantidade = models.IntegerField(null=True, blank=True, default=1)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_minios')
    descricao = models.TextField(null=True, blank=True)
    data_recebimento = models.DateField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_termino = models.DateField(null=True, blank=True)
    status = models.CharField(null=True, blank=True, choices=STATUS, max_length=15, default='nao_iniciado')
    revisao_cliente = models.BooleanField(null=True, blank=True, default=False)
    
    faturamento = models.CharField(max_length=3, null=True, blank= True, choices=FATURAMENTO, default="nao")
    n_nf =models.CharField(max_length=10, null=True, blank=True, default="")

    def __str__(self):
        return self.servico.nome
