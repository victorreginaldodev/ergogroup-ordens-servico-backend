from django.db import models
from .Cliente import Cliente

class Contato(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nome = models.CharField(max_length=30, null=False, blank=False)
    email = models.EmailField(max_length=255, null=True, blank=True)
    telefone = models.CharField(max_length=30, null=True, blank=True)
    observacao = models.TextField(blank=True, null=True, max_length=255)

    def __str__(self):
        return self.nome
