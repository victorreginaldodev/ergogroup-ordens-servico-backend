from django.db import models


class Repositorio(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Repositório'
        verbose_name_plural = 'Repositórios'

    def __str__(self):
        return self.nome
