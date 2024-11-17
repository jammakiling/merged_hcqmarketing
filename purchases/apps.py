from django.apps import AppConfig

class PurchasesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchases'

    def ready(self):
        import purchases.signals  # Import the signals file
