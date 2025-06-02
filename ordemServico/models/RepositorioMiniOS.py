from django.db import models

class RepositorioMiniOS(models.Model):
    nome = models.CharField(max_length=50,)
    descricao = models.TextField(null=True, blank=True,)

    def __str__(self):
        return self.nome