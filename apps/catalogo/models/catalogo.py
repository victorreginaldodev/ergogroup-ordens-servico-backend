from django.db import models


class Complexidade(models.IntegerChoices):
    BAIXA = 1, 'Baixa'
    MEDIA = 2, 'Média'
    ALTA = 3, 'Alta'


class Catalogo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    horas_estimadas = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    complexidade = models.PositiveSmallIntegerField(choices=Complexidade.choices, null=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Catálogo'
        verbose_name_plural = 'Catálogos'

    def __str__(self):
        return self.nome
