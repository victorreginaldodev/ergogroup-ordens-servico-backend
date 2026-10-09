from django.db import models


class Complexidade(models.IntegerChoices):
    BAIXA = 1, 'Baixa'
    MEDIA = 2, 'Média'
    ALTA = 3, 'Alta'


class Catalogo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    setor = models.ForeignKey(
        'organizacoes.Setor',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='catalogos',
    )

    class Meta:
        ordering = ['nome']
        verbose_name = 'Catálogo'
        verbose_name_plural = 'Catálogos'

    def __str__(self):
        return self.nome
