from django.contrib import admin
from apps.servicos.models import Repositorio, Servico


@admin.register(Repositorio)
class RepositorioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['id', 'ordem_servico', 'repositorio', 'status', 'data_conclusao']
    list_filter = ['status']
    search_fields = ['descricao', 'ordem_servico__cliente__nome']
    raw_id_fields = ['ordem_servico', 'repositorio']
