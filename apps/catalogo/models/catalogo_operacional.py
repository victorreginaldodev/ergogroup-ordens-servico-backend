from django.db import models


class CatalogoOperacional(models.Model):
    """Catálogo de serviços disponíveis para Ordens de Serviço Operacionais."""
    nome = models.CharField(max_length=50)
    descricao = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Catálogo Operacional'
        verbose_name_plural = 'Catálogos Operacionais'

    def __str__(self):
        return self.nome
