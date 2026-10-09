from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class MembroSetor(models.Model):
    """Vínculo de um usuário com um setor, exercendo uma função. Um usuário pode estar em vários setores."""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vinculos_setor',
    )
    setor = models.ForeignKey(
        'organizacoes.Setor',
        on_delete=models.PROTECT,
        related_name='membros',
    )
    funcao = models.ForeignKey(
        'organizacoes.Funcao',
        on_delete=models.PROTECT,
        related_name='membros',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['setor__nome', 'usuario__nome_completo']
        verbose_name = 'Membro de setor'
        verbose_name_plural = 'Membros de setor'
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'setor'], name='membro_setor_unico_por_usuario'),
        ]

    def __str__(self):
        return f'{self.usuario} — {self.funcao} em {self.setor}'

    def clean(self):
        if self.setor_id and self.funcao_id and self.setor.organizacao_id != self.funcao.organizacao_id:
            raise ValidationError({'funcao': 'A função precisa ser da mesma organização do setor.'})
