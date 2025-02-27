from django.apps import AppConfig


class ManagementRentalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.management_rentals'
    verbose_name = 'Rental Management'
    
    def ready(self):
        """Import signals when the app is ready."""
        import apps.management_rentals.signals  # noqa