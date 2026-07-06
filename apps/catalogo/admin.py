from django.contrib import admin
from apps.catalogo.models import Catalogo, CatalogoOperacional, SubitemCatalogo


class SubitemCatalogoInline(admin.TabularInline):
    model = SubitemCatalogo
    extra = 0
    fields = ['nome', 'descricao', 'ativo', 'ordem']


@admin.register(Catalogo)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']
    inlines = [SubitemCatalogoInline]


@admin.register(SubitemCatalogo)
class SubitemCatalogoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'catalogo', 'ativo', 'ordem']
    list_filter = ['ativo', 'catalogo']
    search_fields = ['nome', 'descricao', 'catalogo__nome']
    raw_id_fields = ['catalogo']
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(CatalogoOperacional)
class CatalogoOperacionalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']
