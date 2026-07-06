from django.apps import AppConfig


class ServicosConfig(AppConfig):
    """App esvaziado: models/views/serializers migrados para apps.ordens_servico
    e apps.catalogo. Mantido apenas com sua pasta migrations/ intacta — ver
    apps/ordem_servico/apps.py para detalhes.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.servicos'
