from django.apps import AppConfig


class OrdemServicoConfig(AppConfig):
    """App esvaziado: models/views/serializers migrados para apps.ordens_servico.

    Mantido apenas com sua pasta migrations/ intacta, pois o histórico de
    migrations desta app ainda é referenciado (dependencies) por outras apps
    (auditoria, catalogo, ordens_servico). Não remover sem antes reescrever
    essas dependências.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ordem_servico'
