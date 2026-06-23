from django.contrib import admin
from apps.ordem_servico.models import OrdemServico


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'cliente', 'data_criacao', 'status', 'prioridade',
        'valor', 'forma_pagamento', 'contrato', 'liberada_para_faturamento',
        'faturada', 'faturada_por',
    ]
    list_filter = [
        'status', 'prioridade', 'forma_pagamento', 'concluida',
        'faturada', 'cobranca_imediata', 'contrato', 'liberada_para_faturamento',
    ]
    search_fields = ['cliente__nome', 'numero_nf']
    ordering = ['-data_criacao']
    raw_id_fields = ['cliente', 'criado_por', 'atualizado_por', 'liberada_para_faturamento_por', 'faturada_por']
    readonly_fields = [
        'status', 'concluida', 'criada_em', 'data_atualizacao',
        'liberada_para_faturamento', 'liberada_para_faturamento_em',
        'liberada_para_faturamento_por', 'faturada_por',
    ]
