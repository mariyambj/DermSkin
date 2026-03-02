import tensorflow as tf
from tensorflow.keras import mixed_precision
import os

mixed_precision.set_global_policy("mixed_float16")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "densenet169_skin_disease_model.keras")

CLASS_NAMES = [
    "Acne",
    "Eczema",
    "Melanoma",
    "Psoriasis",
    "Rosacea",
    "Vitiligo",
    "Warts",
    "Basal Cell Carcinoma",
    "Seborrheic Keratosis",
    "Normal Skin"
]

model = tf.keras.models.load_model(MODEL_PATH, compile=False)
