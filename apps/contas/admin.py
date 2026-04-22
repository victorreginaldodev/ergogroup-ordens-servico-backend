from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.contas.models import Usuario
from apps.contas.models.choices import TipoUsuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['email', 'nome_completo', 'tipo_usuario', 'ativo', 'is_staff', 'data_criacao']
    list_filter = ['tipo_usuario', 'ativo', 'is_staff', 'is_superuser']
    search_fields = ['email', 'nome_completo', 'username']
    ordering = ['nome_completo']

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Dados pessoais', {'fields': ('nome_completo', 'tipo_usuario')}),
        ('Permissões', {'fields': ('ativo', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'data_criacao')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'nome_completo', 'tipo_usuario', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['data_criacao', 'last_login']
