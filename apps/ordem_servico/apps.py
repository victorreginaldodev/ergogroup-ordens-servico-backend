from django.apps import AppConfig


class OrdemServicoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ordem_servico'

    def ready(self):
        import apps.ordem_servico.signals  # noqa: F401
