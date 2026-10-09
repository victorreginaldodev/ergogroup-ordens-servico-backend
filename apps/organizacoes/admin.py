from django.contrib import admin
from apps.organizacoes.models import Organizacao, Setor


@admin.register(Organizacao)
class OrganizacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'razao_social', 'cnpj', 'cidade', 'uf']
    search_fields = ['nome', 'razao_social', 'cnpj']
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo', 'criado_em']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['criado_em', 'atualizado_em']
