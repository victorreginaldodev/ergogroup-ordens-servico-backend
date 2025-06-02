from django.contrib import admin
from .models import *


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # Exibir essas colunas na listagem
    list_display = ('nome', 'tipo_cliente', 'tipo_inscricao', 'numero_inscricao', 'cliente_ativo')
    
    # Adicionar campos de pesquisa
    search_fields = ('nome', 'numero_inscricao')
    
    # Adicionar filtros laterais
    list_filter = ('tipo_cliente', 'tipo_inscricao', 'cliente_ativo', 'data_criacao')



@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    # Exibir essas colunas na listagem
    list_display = ('nome', 'cliente', 'email', 'telefone')
    
    # Adicionar campos de pesquisa
    search_fields = ('nome', 'cliente__nome', 'email', 'telefone')
    
    # Exibir as informações detalhadas ao editar ou adicionar um contato
    fieldsets = (
        (None, {
            'fields': ('cliente', 'nome', 'email', 'telefone')
        }),
        ('Observações', {
            'fields': ('observacao',),
            'classes': ('collapse',),
        }),
    )


@admin.register(MiniOS)
class MiniOSAdmin(admin.ModelAdmin):
    # Exibir essas colunas na listagem
    list_display = ('cliente', 'servico', 'quantidade', 'profile', 'status', 'data_recebimento', 'data_inicio', 'data_termino')
    
    # Adicionar campos de pesquisa
    search_fields = ('cliente__nome', 'servico__nome', 'profile__nome')
    
    # Adicionar filtros laterais
    list_filter = ('status', 'cliente', 'profile')
    
    # Exibir as informações detalhadas ao editar ou adicionar um MiniOS
    fieldsets = (
        (None, {
            'fields': ('cliente', 'servico', 'quantidade', 'profile', 'descricao')
        }),
        ('Datas', {
            'fields': ('data_recebimento', 'data_inicio', 'data_termino'),
        }),
        ('Status', {
            'fields': ('status',),
            'classes': ('collapse',),
        }),
    )


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    # Exibir essas colunas na listagem
    list_display = ('cliente', 'valor', 'forma_pagamento', 'quantidade_parcelas', 'cobranca_imediata', 'faturamento')
    
    # Adicionar campos de pesquisa
    search_fields = ('cliente__nome',)
    
    # Exibir as informações detalhadas ao editar ou adicionar uma ordem de serviço
    fieldsets = (
        (None, {
            'fields': ('usuario_criador', 'cliente', 'valor', 'forma_pagamento', 'quantidade_parcelas', 'cobranca_imediata', 'data_criacao')
        }),
        ('Faturamento', {
            'fields': ('faturamento_1', 'nome_contato_envio_nf', 'contato_envio_nf', 'faturamento', 'numero_nf', 'data_faturamento'),
        }),
        ('Outros Detalhes', {
            'fields': ('observacao', 'concluida'),
            'classes': ('collapse',),
        }),
    )



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Exibir essas colunas na listagem
    list_display = ('user', 'role',)
    # Adicionar campos de pesquisa
    search_fields = ['user__username']  # Corrigido: agora é uma lista


@admin.register(Repositorio)
class RepositorioAdmin(admin.ModelAdmin):
    # Exibir essas colunas na listagem
    list_display = ('nome', 'descricao')
    
    # Adicionar campos de pesquisa
    search_fields = ('nome', 'descricao')

    # Exibir as informações detalhadas ao editar ou adicionar um repositório
    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao')
        }),
    )


@admin.register(RepositorioMiniOS)
class RepositorioMiniOSAdmin(admin.ModelAdmin):
    # Exibir essas colunas na listagem
    list_display = ('nome', 'descricao',)
    
    # Adicionar campos de pesquisa
    search_fields = ('nome', 'descricao',)
    
    # Exibir as informações detalhadas ao editar ou adicionar um repositório MiniOS
    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao')
        }),
    )


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    # Exibir essas colunas na listagem
    list_display = ('ordem_servico', 'repositorio', 'status', 'data_conclusao')  # Corrigido: Removidos campos inválidos
    
    # Adicionar campos de pesquisa
    search_fields = ('ordem_servico__id', 'ordem_servico__cliente__nome', 'repositorio__nome',)
    
    # Adicionar filtros laterais
    list_filter = ('status', 'ordem_servico__cliente',)
    
    # Exibir as informações detalhadas ao editar ou adicionar um serviço
    fieldsets = (
        (None, {
            'fields': ('ordem_servico', 'repositorio', 'descricao')
        }),
        ('Status e Datas', {
            'fields': ('status', 'data_conclusao'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    # Exibir essas colunas na listagem
    list_display = ('servico', 'profile', 'descricao', 'data_inicio', 'data_termino', 'status')
    
    # Adicionar campos de pesquisa
    search_fields = ('servico__descricao', 'profile__user__username', 'descricao')
    
    # Adicionar filtros laterais
    list_filter = ('status', 'data_inicio', 'data_termino', 'servico', 'profile')
    
    # Exibir as informações detalhadas ao editar ou adicionar uma tarefa
    fieldsets = (
        (None, {
            'fields': ('ordem_servico', 'servico', 'profile', 'descricao')
        }),
        ('Status e Datas', {
            'fields': ('status', 'data_inicio', 'data_termino'),
            'classes': ('collapse',),
        }),
    )
