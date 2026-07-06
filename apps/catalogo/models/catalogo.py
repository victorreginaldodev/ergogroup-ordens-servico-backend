from django.db import models


class Catalogo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Catálogo'
        verbose_name_plural = 'Catálogos'

    def __str__(self):
        return self.nome
