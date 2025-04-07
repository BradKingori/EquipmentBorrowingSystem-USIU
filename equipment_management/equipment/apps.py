from django.apps import AppConfig


class EquipmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'equipment'

    def ready(self):
        import equipment.signals  # Ensure signals are loaded

