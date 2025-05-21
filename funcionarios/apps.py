from django.apps import AppConfig


class FuncionariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'funcionarios'

    def ready(self):
        import funcionarios.signals  # importa señales al iniciar la app
