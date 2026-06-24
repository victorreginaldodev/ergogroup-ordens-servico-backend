from django.contrib import admin
from apps.servicos.models import Repositorio, Servico, SubitemRepositorio


class SubitemRepositorioInline(admin.TabularInline):
    model = SubitemRepositorio
    extra = 0
    fields = ['nome', 'descricao', 'ativo', 'ordem']


@admin.register(Repositorio)
class RepositorioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']
    inlines = [SubitemRepositorioInline]


@admin.register(SubitemRepositorio)
class SubitemRepositorioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'repositorio', 'ativo', 'ordem']
    list_filter = ['ativo', 'repositorio']
    search_fields = ['nome', 'descricao', 'repositorio__nome']
    raw_id_fields = ['repositorio']
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['id', 'ordem_servico', 'repositorio', 'status', 'data_inicio', 'data_termino', 'terminado_por']
    list_filter = ['status']
    search_fields = ['descricao', 'ordem_servico__cliente__nome']
    raw_id_fields = ['ordem_servico', 'repositorio', 'terminado_por']
    readonly_fields = [
        'status', 'data_inicio', 'data_termino', 'data_conclusao',
        'terminado_por', 'criado_em', 'atualizado_em',
    ]
