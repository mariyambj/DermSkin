import os
import numpy as np
from django.shortcuts import render
from django.conf import settings
from PIL import Image

# Import BOTH to handle the version conflict
import keras 
import tensorflow as tf

# Define Class Names
CLASS_NAMES = ['Actinic keratosis', 'Basal cell carcinoma', 'Dermatofibroma', 
               'Melanoma', 'Nevus', 'Pigmented benign keratosis', 
               'Seborrheic keratosis', 'Squamous cell carcinoma', 'Vascular lesion']

def preprocess_image(img):
    img = img.resize((224, 224)) 
    img_array = np.array(img).astype('float32') / 255.0
    return np.expand_dims(img_array, axis=0)

def upload_image(request):
    prediction = None
    if request.method == "POST" and request.FILES.get("image"):
        model_path = os.path.join(settings.BASE_DIR, 'guest', 'model', 'densenet169_skin_disease_model.keras')
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        try:
            # CRITICAL CHANGE: Use keras.models.load_model instead of tf.keras.models.load_model
            model = keras.models.load_model(model_path, compile=False)
        except Exception as e:
            raise RuntimeError(f"Native Keras loader failed. This usually means 'keras' is not installed or version-mismatched. Error: {e}")

        img = Image.open(request.FILES["image"]).convert("RGB")
        processed_img = preprocess_image(img)

        preds = model.predict(processed_img)
        idx = np.argmax(preds)
        
        prediction = {
            "label": CLASS_NAMES[idx],
            "confidence": round(float(preds[0][idx]) * 100, 2)
        }

    return render(request, "guest/upload.html", {"prediction": prediction})

# Other views
def login(request): return render(request, 'guest/login.html')
def registration(request): return render(request, 'guest/registration.html')