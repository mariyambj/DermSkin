from django.shortcuts import render,redirect,get_object_or_404
from clinicadmin.models import *
from .models import *
from django.utils import timezone
from patient.models import *
import base64
from django.core.files.base import ContentFile
from datetime import datetime, timedelta, date
from .models import tbl_schedule, tbl_token
from clinicadmin.models import tbl_doctor
from django.contrib import messages
from .models import tbl_schedule, tbl_token
from patient.models import tbl_appointment
# Create your views here.



def doctor_homepage(request):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('webguest:login')
    doctor = get_object_or_404(tbl_doctor, id=doctor_id)
    today = date.today()
    # Fetch today's NON-CANCELLED appointments
    todays_appointments = tbl_appointment.objects.filter(
        doctor=doctor,
        appointment_date=today
    ).exclude(status="cancelled").order_by('estimated_time')
    # Fetch recent patients WITHOUT cancelled appointments
    recent_patients = tbl_appointment.objects.filter(
        doctor=doctor
    ).exclude(status="cancelled").order_by('-appointment_date')[:5]
    context = {
        'doctor': doctor,
        'todays_count': todays_appointments.count(),
        'pending_reports': 5,
        'avg_time': 15,
        'monthly_earnings': 12500,
        'appointments': todays_appointments,
        'recent_patients': recent_patients,
        'profile_progress': 85
    }
    return render(request, 'doctor/doctor_homepage.html', context)


def doctor_profile(request):
    if 'did' not in request.session:
        return redirect('webguest:login')
    doctor_id = request.session.get('did')
    doctor = tbl_doctor.objects.filter(id=doctor_id).first()

    # 4. Handle the case where the ID in session doesn't exist in the database
    if not doctor:
        messages.error(request, "Doctor record not found.")
        return redirect('login')

    # 5. Success: Render the profile
    return render(request, 'doctor/doctor_profile.html', {'doctor': doctor})

#edit profile
def doctor_editprofile(request):
    if 'did' not in request.session:
        return redirect('webguest:login')
    doctor_id = request.session.get('did')  
    if not doctor_id:
        return redirect('webdoctor:doctor_homepage')  
    doctor = get_object_or_404(tbl_doctor, id=doctor_id)

    if request.method == 'POST':
        doctor.name = request.POST.get('name', doctor.name)
        doctor.age = request.POST.get('age', doctor.age)
        doctor.gender = request.POST.get('gender', doctor.gender)
        doctor.phone_number = request.POST.get('phone_number', doctor.phone_number)
        doctor.address = request.POST.get('address', doctor.address)
        doctor.specialization = request.POST.get('specialization', doctor.specialization)
        doctor.qualification = request.POST.get('qualification', doctor.qualification)
        doctor.medical_registration_number = request.POST.get('medical_registration_number', doctor.medical_registration_number)

        if 'profile_picture' in request.FILES:
            doctor.profile_picture = request.FILES['profile_picture']
        if 'identification' in request.FILES:
            doctor.identification = request.FILES['identification']

        doctor.save()
        return redirect('webdoctor:doctor_profile') 
    return render(request, 'doctor/doctor_editprofile.html', {'doctor': doctor})


def doctor_changepassword(request):
    if 'did' not in request.session:
        return redirect('webguest:login')
    doctor_id=request.session.get('did')
    if not doctor_id:
        return redirect('login')
    doctor=tbl_doctor.objects.get(id=doctor_id)
    if request.method=='POST':
        old_pass=request.POST.get('old_password')
        new_pass=request.POST.get('new_password')
        confirm_pass=request.POST.get('confirm_password')
        if old_pass!=doctor.password:
            return render(request,'doctor/doctor_changepassword.html',{'error':'Old password is incorrect'})
        if new_pass!= confirm_pass:
            return render(request,'doctor/doctor_changepassword.html',{'error':'New Password doesnot match'})
        doctor.password=new_pass
        doctor.save()

        return render(request,'doctor/doctor_changepassword.html',{'Sucess':'Password updated succesfully'})
    return render(request, 'doctor/doctor_changepassword.html')




def doctor_schedule(request):
    # 1. Get ID from session and verify the doctor exists FIRST
    doctor_id = request.session['did']
    if not doctor_id:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('webguest:login')
    try:
        doctor = tbl_doctor.objects.get(id=doctor_id)
    except tbl_doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('webguest:login')
    # 2. Handle the Form Submission
    if request.method == 'POST':
        schedule_date = request.POST.get('schedule_date')
        day_of_week = request.POST.get('day_of_week')
        is_leave = request.POST.get('is_leave') == 'on'
        if is_leave:
            if tbl_schedule.objects.filter(doctor=doctor, schedule_date=schedule_date).exists():
                messages.error(request, "A schedule already exists for this date. Please delete it first from 'View Schedules'.")
                return redirect('webdoctor:doctor_schedule')
            tbl_schedule.objects.create(
                doctor=doctor,
                schedule_date=schedule_date,
                day_of_week=day_of_week,
                is_available=False
            )
            messages.success(request, f"Leave allocated successfully for {schedule_date}.")
            return redirect('webdoctor:doctor_schedule')
        # Normal Shift Generation
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        if not start_time_str or not end_time_str:
            messages.error(request, "Start time and end time are required.")
            return redirect('webdoctor:doctor_schedule')
        try:
            consultation_duration = int(request.POST.get('consultation_duration'))
            total_patients = int(request.POST.get('total_patients'))
        except (ValueError, TypeError):
            messages.error(request, "Please provide valid numbers for consultation duration and total patients.")
            return redirect('webdoctor:doctor_schedule')

        # ── Break Time Logic ──────────────────────────────────────────────────
        fmt = '%H:%M'
        start_dt = datetime.strptime(start_time_str, fmt)
        end_dt   = datetime.strptime(end_time_str,   fmt)
        BREAK_CUTOFF_START = datetime.strptime('12:30', fmt)  # 12:30 PM
        BREAK_CUTOFF_END   = datetime.strptime('13:00', fmt)  # 1:00 PM
        # Only ask/use break times if the shift actually spans the lunch window
        needs_break = start_dt < BREAK_CUTOFF_START and end_dt > BREAK_CUTOFF_END
        if needs_break:
            # Use whatever the doctor submitted from the form
            break_start_str = request.POST.get('break_start_time', '').strip() or None
            break_end_str   = request.POST.get('break_end_time',   '').strip() or None
        else:
            # Shift doesn't span lunch — ignore form values, store NULL
            break_start_str = None
            break_end_str   = None
        # Check if schedule exists on this day to avoid duplicates
        if tbl_schedule.objects.filter(doctor=doctor, schedule_date=schedule_date).exists():
            messages.error(request, "A schedule already exists for this date. Please delete it first from 'View Schedules'.")
            return redirect('webdoctor:doctor_schedule')
        # Save the main Schedule record
        schedule = tbl_schedule.objects.create(
            doctor=doctor,
            schedule_date=schedule_date,
            day_of_week=day_of_week,
            start_time=start_time_str,
            end_time=end_time_str,
            consultation_duration=consultation_duration,
            total_patients=total_patients,
            break_start_time=break_start_str if break_start_str else None,
            break_end_time=break_end_str if break_end_str else None,
        )
        # Time Calculations for Tokens
        current_time = start_dt
        break_start = datetime.strptime(break_start_str, fmt) if break_start_str else None
        break_end   = datetime.strptime(break_end_str,   fmt) if break_end_str   else None
        # Generate Tokens Loop
        for i in range(1, total_patients + 1):
            # Fast-forward past the break window if we hit it
            if break_start and break_end and break_start <= current_time < break_end:
                current_time = break_end
            tbl_token.objects.create(
                doctor=doctor,
                schedule=schedule,
                date=schedule_date,
                day_of_week=day_of_week,
                token_number=i,
                estimated_time=current_time.time(),
                is_booked=False
            )
            current_time += timedelta(minutes=consultation_duration)
        messages.success(request, f"Schedule saved! {total_patients} tokens successfully generated.")
        return redirect('webdoctor:doctor_schedule')
    # 3. GET request — just render the page
    return render(request, 'doctor/schedule.html')
 


def doctor_view_schedule(request):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('webguest:login')
    doctor = get_object_or_404(tbl_doctor, id=doctor_id)
    today = timezone.localdate()
    schedules = tbl_schedule.objects.filter(
        doctor=doctor,
        schedule_date__gte=today
    ).order_by('schedule_date')
    schedule_list = []
    for s in schedules:
        if not s.is_available:
            # Leave day — no tokens needed
            schedule_list.append({
                'schedule': s,
                'is_leave': True,
                'total_tokens': 0,
                'booked_tokens': 0,
                'available_tokens': 0,
            })
        else:
            tokens = tbl_token.objects.filter(schedule=s)
            booked_count = tokens.filter(is_booked=True).count()
            schedule_list.append({
                'schedule': s,
                'is_leave': False,
                'total_tokens': tokens.count(),
                'booked_tokens': booked_count,
                'available_tokens': tokens.count() - booked_count,
            })
    return render(request, 'doctor/view_schedule.html', {'schedules': schedule_list})


def delete_schedule(request, id):
    schedule = get_object_or_404(tbl_schedule, id=id)
    # Check if any tokens are booked
    if tbl_token.objects.filter(schedule=schedule, is_booked=True).exists():
        messages.error(request, "Cannot delete schedule as some tokens are already booked.")
    else:
        schedule.delete()
        messages.success(request, "Schedule deleted successfully.")
    return redirect('webdoctor:doctor_view_schedule')


#view bookings

def doctor_patient_bookings(request):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('webguest:login')
    doctor = get_object_or_404(tbl_doctor, id=doctor_id)
    status_filter = request.GET.get('status')
    today = timezone.localdate()
    # show only confirmed and pending
    appointments = tbl_appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=today,
        status__in=['confirmed', 'pending']
    )
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    appointments = appointments.order_by('appointment_date', 'estimated_time')
    return render(request, 'doctor/patient_bookings.html', {
        'appointments': appointments,
        'current_status': status_filter
    })


#doctor reports
def doctor_reports(request):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('webguest:login')
    doctor = get_object_or_404(tbl_doctor, id=doctor_id)
    from patient.models import tbl_appointment, tbl_feedback
    from django.db.models import Avg

    total_appointments = tbl_appointment.objects.filter(doctor=doctor).count()
    completed_appointments = tbl_appointment.objects.filter(doctor=doctor, status='completed').count()
    cancelled_appointments = tbl_appointment.objects.filter(doctor=doctor, status='cancelled').count()

    # Rating stats
    feedbacks = tbl_feedback.objects.filter(doctor=doctor)
    total_reviews = feedbacks.count()
    avg_rating = feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)

    rating_distribution = []
    for star in range(5, 0, -1):
        count = feedbacks.filter(rating=star).count()
        percentage = round((count / total_reviews * 100)) if total_reviews > 0 else 0
        rating_distribution.append({'star': star, 'count': count, 'percentage': percentage})

    # Monthly breakdown (last 6 months)
    today = date.today()
    monthly_stats = []
    for i in range(6):
        month = today.month - i
        year = today.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        month_start = date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        count = tbl_appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=month_start,
            appointment_date__lt=next_month
        ).count()
        monthly_stats.append({'month': month_start.strftime('%B %Y'), 'count': count})

    monthly_stats_chart = list(reversed(monthly_stats))

    context = {
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'monthly_stats': monthly_stats,
        'monthly_stats_chart': monthly_stats_chart,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'rating_distribution': rating_distribution,
    }
    return render(request, 'doctor/doctor_reports.html', context)




def patient_details(request, id):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('webguest:login')
    from patient.models import tbl_appointment, tbl_report
    appointment = get_object_or_404(tbl_appointment, id=id, doctor_id=doctor_id)
    # Change status when doctor opens patient details
    if appointment.status == 'confirmed':
        appointment.status = 'pending'
        appointment.save()
    # Fetch previous reports
    reports = tbl_report.objects.filter(patient=appointment.patient).order_by('-report_date')
    return render(request, 'doctor/patient_details.html', {
        'appointment': appointment,
        'reports': reports
    })


#report
'''def doctor_save_report(request):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('webguest:login')
    if request.method == 'POST':
        from patient.models import tbl_patient, tbl_report
        patient_id = request.POST.get('patient_id')
        image_data = request.POST.get('image_data')
        disease = request.POST.get('disease')
        confidence = request.POST.get('confidence')
        patient = get_object_or_404(tbl_patient, id=patient_id)
        report = tbl_report(
            patient=patient,
            disease=disease,
            confidence=confidence
        )
        if image_data and ';base64,' in image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'report_{patient.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.{ext}')
            report.image.save(f'report.{ext}', data, save=False)
            
        report.save()
        messages.success(request, "Patient report generated and saved successfully!")
        # We need to find an appointment ID to redirect back to patient_details
        from patient.models import tbl_appointment
        # ── Mark the appointment as completed ──────────────────────────
        latest_appointment = tbl_appointment.objects.filter(
            patient=patient,
            doctor_id=doctor_id,
            status__in=['pending', 'confirmed']
        ).order_by('-appointment_date', '-token_number').first()

        if latest_appointment:
            latest_appointment.status = 'completed'
            latest_appointment.save()
            return redirect('webdoctor:patient_details', id=latest_appointment.id)
    return redirect('webdoctor:doctor_homepage')'''


# report
'''def doctor_save_report(request):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('webguest:login')
    if request.method == 'POST':
        from patient.models import tbl_patient, tbl_report, tbl_appointment
        patient_id = request.POST.get('patient_id')
        image_data = request.POST.get('image_data')
        disease = request.POST.get('disease')
        confidence = request.POST.get('confidence')
        patient = get_object_or_404(tbl_patient, id=patient_id)
        # Get latest appointment
        latest_appointment = tbl_appointment.objects.filter(
            patient=patient,
            doctor_id=doctor_id,
            status__in=['pending', 'confirmed']
        ).order_by('-appointment_date', '-token_number').first()
        # Create report and attach appointment
        report = tbl_report(
            patient=patient,
            appointment=latest_appointment,
            disease=disease,
            confidence=confidence
        )
        # Save image
        if image_data and ';base64,' in image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'report_{patient.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.{ext}'
            )
            report.image.save(f'report.{ext}', data, save=False)
        report.save()
        # Mark appointment completed
        if latest_appointment:
            latest_appointment.status = 'completed'
            latest_appointment.save()

            messages.success(request, "Patient report generated and saved successfully!")
            return redirect('webdoctor:patient_details', id=latest_appointment.id)
    return redirect('webdoctor:doctor_homepage')'''


def doctor_save_report(request):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('webguest:login')
    if request.method == 'POST':
        from patient.models import tbl_patient, tbl_report, tbl_appointment
        patient_id = request.POST.get('patient_id')
        image_data = request.POST.get('image_data')
        disease = request.POST.get('disease')
        confidence = request.POST.get('confidence')
        prescription = request.POST.get('prescription', '').strip()  # ← new
        patient = get_object_or_404(tbl_patient, id=patient_id)
        latest_appointment = tbl_appointment.objects.filter(
            patient=patient,
            doctor_id=doctor_id,
            status__in=['pending', 'confirmed']
        ).order_by('-appointment_date', '-token_number').first()
        report = tbl_report(
            patient=patient,
            appointment=latest_appointment,
            disease=disease,
            confidence=confidence,
            prescription=prescription  # ← new
        )
        if image_data and ';base64,' in image_data:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr),
                name=f'report_{patient.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}.{ext}'
            )
            report.image.save(f'report.{ext}', data, save=False)
        report.save()
        if latest_appointment:
            latest_appointment.status = 'completed'
            latest_appointment.save()
        messages.success(request, "Patient report generated and saved successfully!")
        return redirect('webdoctor:patient_details', id=latest_appointment.id)
    return redirect('webdoctor:doctor_homepage')




import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings

# 1. Define the exact class names in ALPHABETICAL order
# (This matches how PyTorch's ImageFolder sorted them during training)
CLASS_NAMES = [
    "Atopic Dermatitis", "Basal Cell Carcinoma", "Benign Keratosis",
    "Eczema", "Melanocytic Nevi", "Melanoma", "Psoriasis",
    "Seborrheic Keratoses", "Tinea Ringworm", "Warts Molluscum"
]

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 2. Rebuild the exact model architecture
def build_model(num_classes=10):
    model = models.densenet169(weights=None) # We don't need internet to download weights here
    in_features = model.classifier.in_features
    
    # Must match your "Extreme Regularization" structure exactly
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.6, inplace=True), 
        nn.Linear(in_features, 512),
        nn.BatchNorm1d(512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.5),               
        nn.Linear(512, num_classes)
    )
    return model

# Initialize the model globally so it doesn't reload on every single web request
MODEL_PATH = os.path.join(settings.BASE_DIR, 'doctor', 'dl_model', 'best_densenet_mixup.pth')
model = build_model(len(CLASS_NAMES))
# Load weights safely (map_location ensures it works even on a CPU-only server)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval() # Set to evaluation mode!

# 3. Define the Image Transform (Must match your val_tf)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

def predict_disease(request):
    context = {}
    pid = request.GET.get('pid')
    if pid:
        context['pid'] = pid
    
    if request.method == 'POST' and request.FILES.get('skin_image'):
        uploaded_file = request.FILES['skin_image']
        
        # Read file for base64 encoding (needs to be reset for FileSystemStorage)
        file_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        import base64
        b64_str = base64.b64encode(file_bytes).decode('utf-8')
        # Handle cases where content_type is not accurately set
        content_type = getattr(uploaded_file, 'content_type', 'image/jpeg')
        context['image_data'] = f"data:{content_type};base64,{b64_str}"

        # Save the file temporarily to display it on the HTML page
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        uploaded_file_url = fs.url(filename)
        context['image_url'] = uploaded_file_url
        
        # Process the image for PyTorch
        try:
            # Open image and convert to RGB (removes alpha channels from PNGs)
            img = Image.open(fs.path(filename)).convert('RGB')
            img_tensor = transform(img).unsqueeze(0).to(DEVICE) # Add batch dimension
            
            # Make Prediction
            with torch.no_grad():
                outputs = model(img_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
                confidence, predicted_idx = torch.max(probabilities, 0)
                
                predicted_class = CLASS_NAMES[predicted_idx.item()]
                confidence_score = round(confidence.item() * 100, 2)
                
                context['predicted_class'] = predicted_class
                context['confidence'] = confidence_score
                
        except Exception as e:
            context['error'] = f"Error processing image: {str(e)}"
            
    return render(request, 'doctor/predict.html', context)