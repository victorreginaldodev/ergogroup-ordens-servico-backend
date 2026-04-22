from django.contrib import admin
from apps.ordem_servico.models import OrdemServico


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'data_criacao', 'valor', 'forma_pagamento', 'concluida', 'faturada']
    list_filter = ['forma_pagamento', 'concluida', 'faturada', 'cobranca_imediata']
    search_fields = ['cliente__nome', 'numero_nf']
    ordering = ['-data_criacao']
    raw_id_fields = ['cliente', 'criado_por']
