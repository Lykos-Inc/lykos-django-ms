from django.apps import AppConfig

class CatalogConfig(AppConfig): # Sugestão: Mude de CoreConfig para CatalogConfig
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'