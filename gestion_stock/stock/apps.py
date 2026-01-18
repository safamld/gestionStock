from django.apps import AppConfig


class StockConfig(AppConfig):
    name = 'stock'
    
    def ready(self):
        """
        Enregistre les signaux Django quand l'application est prête.
        """
        import stock.signals  # noqa
