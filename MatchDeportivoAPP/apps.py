from django.apps import AppConfig


class MatchdeportivoappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MatchDeportivoAPP'



from django.apps import AppConfig

class MatchdeportivoappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MatchDeportivoAPP'

    def ready(self):
        import MatchDeportivoAPP.signals
