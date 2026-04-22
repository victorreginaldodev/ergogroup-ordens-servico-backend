from django.apps import AppConfig


class OrdemservicoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'legado.ordemServico'

    def ready(self):
        import legado.ordemServico.signals