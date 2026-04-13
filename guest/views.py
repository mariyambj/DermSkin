import os
import numpy as np
import torch
import random
import keras
import tensorflow as tf
from django.shortcuts import render,redirect
from django.conf import settings
from PIL import Image
from .models import *
from django.contrib.auth.hashers import check_password
from clinicadmin.models import tbl_admin,tbl_doctor
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from patient.models import tbl_appointment



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
#'skin_disease_model_deploy.keras',
_MODEL = None

def _get_model():
    global _MODEL
    if _MODEL is None:
        model_path = os.path.join(
            settings.BASE_DIR, 'guest', 'model', 'skin_disease_model_deploy.keras'
        )
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        _MODEL = keras.models.load_model(model_path, compile=False)
    return _MODEL

'''def _get_model():
    global _MODEL
    if _MODEL is None:
        model_path = os.path.join(
            settings.BASE_DIR, 'guest', 'model', 'best_densenet.pth'
        )
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        # Load full PyTorch model
        _MODEL = torch.load(model_path, map_location="cpu")
    return _MODEL'''


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
    pid = request.GET.get('pid') or request.POST.get('pid')
    #appointment = tbl_appointment.objects.get(patient_id=pid)
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
        "pid": pid,
    })


# login
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
        elif admin_count>0:
            admin_data=tbl_admin.objects.get(email=email,password=password)
            request.session['aid']=admin_data.id
            return redirect('webadmin:admin_homepage')
        elif doctor_count>0:
            doctor_data=tbl_doctor.objects.get(email=email,password=password)
            request.session['did']=doctor_data.id
            return redirect('webdoctor:doctor_homepage')
        else:
            messages.error(request, "Invalid Email or Password")
    return render(request, 'guest/login.html')



#patient registration
'''def registration(request):
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
    return render(request, 'guest/patient_registration.html')'''



from .models import tbl_patient

# Patient Registration
def registration(request):
    if request.method == 'POST':
        first_name = request.POST.get('txt_name')
        address = request.POST.get('txt_address')
        phone = request.POST.get('txt_phone')
        email = request.POST.get('txt_email')
        age = request.POST.get('txt_age')
        gender = request.POST.get('txt_gender')
        password = request.POST.get('txt_password')
        repassword = request.POST.get('txt_repassword')
        if password != repassword:
            return render(request,'guest/patient_registration.html',{'error':'Password do not match'})
                # Check if email already exists
        if tbl_patient.objects.filter(email=email).exists():
            return render(request, 'guest/patient_registration.html',
                          {'error': 'Email already registered'})
        # Check if phone already exists
        if tbl_patient.objects.filter(phone=phone).exists():
            return render(request, 'guest/patient_registration.html',
                          {'error': 'Phone number already registered'})
        # generate OTP
        otp = random.randint(1000,9999)
        # store data in session
        request.session['otp'] = otp
        request.session['first_name'] = first_name
        request.session['address'] = address
        request.session['phone'] = phone
        request.session['email'] = email
        request.session['age'] = age
        request.session['gender'] = gender
        request.session['password'] = password
        # send OTP email
        send_mail(
            'Your Registration OTP',
            f'Your OTP for registration is {otp}',
            'yourgmail@gmail.com',
            [email],
            fail_silently=False,
        )
        return redirect('webguest:verify_otp')
    return render(request, 'guest/patient_registration.html')


#otp verification view
def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        if str(user_otp) == str(session_otp):
            patient = tbl_patient(
                first_name = request.session.get('first_name'),
                address = request.session.get('address'),
                phone = request.session.get('phone'),
                email = request.session.get('email'),
                age = request.session.get('age'),
                gender = request.session.get('gender'),
                pass_word = request.session.get('password')
            )
            patient.save()
            return redirect('webguest:login')
        else:
            return render(request,'guest/verify_otp.html',{'error':'Invalid OTP'})
    return render(request,'guest/verify_otp.html')


#resend otp
def resend_otp(request):
    email = request.session.get('email')
    if not email:
        return redirect('webguest:registration')
    otp = random.randint(100000, 999999)
    request.session['otp'] = otp
    send_mail(
        'Your New OTP Code',
        f'Your new verification OTP is {otp}',
        'yourgmail@gmail.com',
        [email],
        fail_silently=False
    )
    return redirect('webguest:verify_otp')


#patient list
def patient_list(request):
    patients=tbl_patient.objects.all()
    return render(request,'guest/patient_list.html',{'patients':patients})

def home_page(request):
    return render(request,'guest/home_page.html')


#send otp for forgetpassword
def send_otp(request):
    if request.method == "POST":
        email = request.POST.get('email')
        user = None
        role = None
        # check doctor
        if tbl_doctor.objects.filter(email=email).exists():
            user = tbl_doctor.objects.get(email=email)
            role = "doctor"
        # check patient
        elif tbl_patient.objects.filter(email=email).exists():
            user = tbl_patient.objects.get(email=email)
            role = "patient"
        # check admin
        elif tbl_admin.objects.filter(email=email).exists():
            user = tbl_admin.objects.get(email=email)
            role = "admin"
        else:
            messages.error(request,"Email not registered")
            return redirect('webguest:login')
        otp = random.randint(100000,999999)
        request.session['reset_otp'] = otp
        request.session['reset_email'] = email
        request.session['reset_role'] = role
        send_mail(
            "Password Reset OTP",
            f"Your OTP for resetting password is: {otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )
        return redirect('webguest:verify_otp_forget')
    

#otp for forget password
def verify_otp_forget(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('reset_otp')
        if str(entered_otp) == str(session_otp):
            return redirect('webguest:new_password')
        else:
            messages.error(request,"Invalid OTP")
    return render(request,'guest/verify_otp.html')


#for forget password
def new_password(request):
    email = request.session.get('reset_email')
    role = request.session.get('reset_role')
    if request.method == "POST":
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            messages.error(request,"Passwords do not match")
            return redirect('webguest:new_password')
        if role == "doctor":
            user = tbl_doctor.objects.get(email=email)
            user.password = new_password
            user.save()
        elif role == "patient":
            user = tbl_patient.objects.get(email=email)
            user.pass_word = new_password
            user.save()
        elif role == "admin":
            user = tbl_admin.objects.get(email=email)
            user.password = new_password
            user.save()
        messages.success(request,"Password updated successfully")
        return redirect('webguest:login')
    return render(request,'guest/new_password.html')