from django.contrib import admin
from apps.tarefas.models import RepositorioMiniOS, Tarefa, MiniOS


@admin.register(RepositorioMiniOS)
class RepositorioMiniOSAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['id', 'servico', 'responsavel', 'status', 'data_inicio', 'data_termino']
    list_filter = ['status']
    search_fields = ['descricao', 'responsavel__nome_completo']
    raw_id_fields = ['servico', 'responsavel']
    readonly_fields = ['data_inicio', 'data_termino', 'criada_em', 'atualizado_em']


@admin.register(MiniOS)
class MiniOSAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'cliente', 'servico', 'responsavel', 'status',
        'gera_cobranca', 'faturada', 'faturada_por', 'data_recebimento',
    ]
    list_filter = ['status', 'faturada', 'revisao_cliente', 'gera_cobranca']
    search_fields = ['cliente__nome', 'servico__nome', 'responsavel__nome_completo']
    raw_id_fields = ['cliente', 'servico', 'responsavel', 'liberada_cobranca_por', 'faturada_por']
    readonly_fields = [
        'data_inicio', 'data_termino', 'criada_em', 'atualizado_em',
        'gera_cobranca', 'data_liberacao_cobranca',
        'liberada_cobranca_por', 'faturada_por',
    ]
