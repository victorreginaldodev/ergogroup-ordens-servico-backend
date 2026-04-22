from django.db import models


class RepositorioMiniOS(models.Model):
    """Catálogo de serviços disponíveis para Mini Ordens de Serviço."""
    nome = models.CharField(max_length=50)
    descricao = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Repositório Mini OS'
        verbose_name_plural = 'Repositórios Mini OS'

    def __str__(self):
        return self.nome
