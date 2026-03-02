import os
from django.apps import AppConfig
from django.conf import settings
from tensorflow.keras.models import load_model

class GuestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'guest'
    model = None

    def ready(self):
        # Matches your screenshot structure: guest -> model -> file
        model_path = os.path.join(settings.BASE_DIR, 'guest', 'models', 'restored.keras')
        if os.path.exists(model_path):
            GuestConfig.model = load_model(model_path, compile=False)