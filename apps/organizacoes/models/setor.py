from django.db import models


class Setor(models.Model):
    organizacao = models.ForeignKey(
        'organizacoes.Organizacao',
        on_delete=models.PROTECT,
        related_name='setores',
    )
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Setor'
        verbose_name_plural = 'Setores'
        constraints = [
            models.UniqueConstraint(fields=['organizacao', 'nome'], name='setor_nome_unico_por_organizacao'),
        ]

    def __str__(self):
        return self.nome
