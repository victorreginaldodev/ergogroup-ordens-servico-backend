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


@admin.register(MiniOS)
class MiniOSAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'servico', 'responsavel', 'status', 'faturada', 'data_recebimento']
    list_filter = ['status', 'faturada', 'revisao_cliente']
    search_fields = ['cliente__nome', 'servico__nome', 'responsavel__nome_completo']
    raw_id_fields = ['cliente', 'servico', 'responsavel']
