from django.db import models


class SubitemRepositorio(models.Model):
    repositorio = models.ForeignKey(
        'servicos.Repositorio',
        on_delete=models.CASCADE,
        related_name='subitens',
    )
    nome = models.CharField(max_length=150)
    descricao = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['repositorio__nome', 'ordem', 'nome']
        verbose_name = 'Subitem de repositorio'
        verbose_name_plural = 'Subitens de repositorio'
        constraints = [
            models.UniqueConstraint(
                fields=['repositorio', 'nome'],
                name='unique_subitem_por_repositorio',
            ),
        ]

    def __str__(self):
        return f'{self.repositorio} - {self.nome}'
