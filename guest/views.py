import os
import numpy as np
from django.shortcuts import render,redirect
from django.conf import settings
from PIL import Image
from .models import *
from django.contrib.auth.hashers import check_password
from clinicadmin.models import tbl_admin,tbl_doctor

import keras
import tensorflow as tf

# =====================================================================
# CLASS NAMES — must match alphabetical folder order used during training
# (tf.keras.utils.image_dataset_from_directory sorts class folders A–Z)
# Dataset: ismailpromus/skin-diseases-image-dataset  (10 classes)
# =====================================================================
CLASS_NAMES = [
    '1. Eczema 1677',
    '10. Warts Molluscum and other Viral Infections - 2103',
    '2. Melanoma 15.75k',
    '3. Atopic Dermatitis - 1.25k',
    '4. Basal Cell Carcinoma (BCC) 3323',
    '5. Melanocytic Nevi (NV) - 7970',
    '6. Benign Keratosis-like Lesions (BKL) 2624',
    '7. Psoriasis pictures Lichen Planus and related diseases - 2k',
    '8. Seborrheic Keratoses and other Benign Tumors - 1.8k',
    '9. Tinea Ringworm Candidiasis and other Fungal Infections - 1.7k',
]

# Friendly display names for the same order
DISPLAY_NAMES = [
    'Eczema',
    'Warts / Molluscum & Viral Infections',
    'Melanoma',
    'Atopic Dermatitis',
    'Basal Cell Carcinoma (BCC)',
    'Melanocytic Nevi (Moles)',
    'Benign Keratosis-like Lesions',
    'Psoriasis / Lichen Planus & Related',
    'Seborrheic Keratoses & Benign Tumors',
    'Tinea / Ringworm / Candidiasis & Fungal Infections',
]

# =====================================================================
# Load model ONCE at module import — avoids reloading on every request
# =====================================================================
_MODEL = None

def _get_model():
    global _MODEL
    if _MODEL is None:
        model_path = os.path.join(
            settings.BASE_DIR, 'guest', 'models', 'skin_disease_model_deploy.keras'
        )
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        _MODEL = keras.models.load_model(model_path, compile=False)
    return _MODEL


def preprocess_image(img):
    """
    Resize to 224×224 and convert to a uint8 batch (0–255).
    The model already contains a Rescaling(1./255) layer, so do NOT
    divide by 255 here — doing so a second time collapses all pixel
    values near zero and destroys predictions.
    """
    img = img.resize((224, 224))
    img_array = np.array(img, dtype='float32')   # keep 0–255 range
    return np.expand_dims(img_array, axis=0)


def upload_image(request):
    prediction = None
    image_data = None          # base64 data-URL shown in the result section

    if request.method == "POST" and request.FILES.get("image"):
        import base64, io

        uploaded = request.FILES["image"]

        # ── Encode original image for display ──────────────────────────
        uploaded.seek(0)
        img_bytes = uploaded.read()
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        mime = uploaded.content_type or "image/jpeg"
        image_data = f"data:{mime};base64,{b64}"

        # ── Run inference ───────────────────────────────────────────────
        uploaded.seek(0)
        model = _get_model()
        img = Image.open(uploaded).convert("RGB")
        processed_img = preprocess_image(img)

        preds = model.predict(processed_img)
        idx = int(np.argmax(preds[0]))

        prediction = {
            "label": DISPLAY_NAMES[idx],
            "raw_label": CLASS_NAMES[idx],
            "confidence": round(float(preds[0][idx]) * 100, 2),
        }

    return render(request, "guest/upload.html", {
        "prediction": prediction,
        "image_data": image_data,
    })


# Other views
def login(request):
    if request.method=='POST':
        email=request.POST.get('txt_email')
        password=request.POST.get('txt_password')
        patient_count=tbl_patient.objects.filter(email=email,pass_word=password).count()
        admin_count=tbl_admin.objects.filter(email=email,password=password).count()
        doctor_count=tbl_doctor.objects.filter(email=email,password=password).count()
        if patient_count>0:
            patient_data=tbl_patient.objects.get(email=email,pass_word=password)
            request.session['pid']=patient_data.id
            return redirect('webpatient:patient_homepage')
        if admin_count>0:
            admin_data=tbl_admin.objects.get(email=email,password=password)
            request.session['aid']=admin_data.id
            return redirect('webadmin:admin_homepage')
        if doctor_count>0:
            doctor_data=tbl_doctor.objects.get(email=email,password=password)
            request.session['did']=doctor_data.id
            return redirect('webdoctor:doctor_homepage')
   
    return render(request, 'guest/login.html')



#patient registration
def registration(request):
    if request.method=='POST':
        first_name=request.POST.get('txt_name')
        address=request.POST.get('txt_address')
        phone=request.POST.get('txt_phone')
        email=request.POST.get('txt_email')
        age=request.POST.get('txt_age')
        gender=request.POST.get('txt_gender')
        password=request.POST.get('txt_password')
        repassword=request.POST.get('txt_repassword')
        if password!= repassword:
            return render(request,'guest/patient_registration.html',{'error':'Password do not match'})
        patient=tbl_patient(first_name=first_name,
                            address=address,
                            phone=phone,
                            email=email,
                            age=age,
                            pass_word=password,
                            gender=gender)
        patient.save()
        return redirect('webguest:registration')
    return render(request, 'guest/patient_registration.html')


#patient list

def patient_list(request):
    patients=tbl_patient.objects.all()
    return render(request,'guest/patient_list.html',{'patients':patients})

def home_page(request):
    return render(request,'guest/home_page.html')