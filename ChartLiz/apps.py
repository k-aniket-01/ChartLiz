# apps.py
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ChartLiz'

    def ready(self):
        import ChartLiz.signals  # make sure this line is here
