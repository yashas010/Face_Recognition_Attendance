# core/apps.py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """Run setup tasks when the app is ready."""
        from core.arcface_model import load_employee_embeddings
        load_employee_embeddings()
