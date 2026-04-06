from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from guest.models import *
from doctor.models import *
from clinicadmin.models import *
from .models import *
from datetime import datetime, timedelta, time, date
import base64
from django.core.files.base import ContentFile



#homepage
def home_page(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')

    patient = tbl_patient.objects.get(id=patient_id)
    appointments = tbl_appointment.objects.filter(patient=patient)
    
    context = {
        'patient': patient,
        'total_appointments': appointments.count(),
        'upcoming_appointments': appointments.filter(appointment_date__gte=date.today(), status='confirmed').count(),
        'prescriptions': 2, # Placeholder or fetch from medical records if available
        'reports_ready': 1,  # Placeholder or fetch from medical records if available
        'recent_appointments': appointments.order_by('-appointment_date')[:5],
        'doctors': tbl_doctor.objects.all()[:3]
    }
    return render(request, 'patient/home.html', context)


#Patient Profile

def patient_profile(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('login')
    patient = get_object_or_404(tbl_patient, id=patient_id)
    return render(request, 'patient/patient_profile.html', {'patient': patient})


def edit_profile(request):
    patient_id=request.session.get('pid')
    if not patient_id:
        return redirect('login')
    patient=tbl_patient.objects.get(id=patient_id)
    if request.method=='POST':
        patient.first_name = request.POST.get('txt_name')
        patient.address = request.POST.get('txt_address')
        patient.phone = request.POST.get('txt_phone')
        patient.age = request.POST.get('txt_age')
        patient.gender = request.POST.get('txt_gender')
        patient.save()
        return redirect('patient_homepage')
    return render(request, 'patient/edit_profile.html', {'patient': patient})


def change_password(request):
    patient_id=request.session.get('pid')
    if not patient_id:
        return redirect('login')
    patient=tbl_patient.objects.get(id=patient_id)
    if request.method=='POST':
        old_pass=request.POST.get('old_password')
        new_pass=request.POST.get('new_password')
        confirm_pass=request.POST.get('confirm_password')
        if old_pass!=patient.pass_word:
            return render(request,'patient/change_password.html',{'error':'Old password is incorrect'})
        if new_pass!= confirm_pass:
            return render(request,'patient/change_password.html',{'error':'New Password doesnot match'})
        patient.pass_word=new_pass
        patient.save()

        return render(request,'patient/change_password.html',{'Sucess':'Password updated succesfully'})
    return render(request, 'patient/change_password.html')


#view doctor

def doctor_list(request):
    doctors = tbl_doctor.objects.all()
    return render(request,'patient/doctor_list.html',{
        'doctors':doctors
    })

def doctor_details(request, id):
    doctor = get_object_or_404(tbl_doctor, id=id)
    return render(request, 'patient/view_details.html', {
        'doctor': doctor
    })


#Booking


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import date

from doctor.models import tbl_token
from patient.models import tbl_appointment, tbl_patient
from clinicadmin.models import tbl_doctor


# ==========================================
# BOOK APPOINTMENT PAGE (SHOW TOKENS)
# ==========================================
def book_appointment(request, doctor_id):

    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')

    doctor = get_object_or_404(tbl_doctor, id=doctor_id)

    selected_date = request.GET.get('appointment_date')

    if not selected_date:
        selected_date = date.today()

    tokens = tbl_token.objects.filter(
        doctor_id=doctor_id,
        date=selected_date
    ).order_by('token_number')

    context = {
        'tokens': tokens,
        'doctor': doctor,
        'selected_date': selected_date
    }
    return render(request, 'patient/booking_appointment.html', context)


# ==========================================
# CONFIRM BOOKING
# ==========================================
def confirm_booking(request, token_id):
    token = get_object_or_404(tbl_token, id=token_id)
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')
    patient = get_object_or_404(tbl_patient, id=patient_id)
    if request.method == "POST":
        if token.is_booked:
            messages.error(request, "Sorry, this token is already booked.")
            return redirect('webpatient:book_appointment', doctor_id=token.doctor.id)
        symptoms = request.POST.get('symptoms')
        tbl_appointment.objects.create(
            patient=patient,
            doctor=token.doctor,
            appointment_date=token.date,
            token_number=token.token_number,
            estimated_time=token.estimated_time,
            symptoms=symptoms,
            status='confirmed'
        )
        token.is_booked = True
        token.save()
        messages.success(request, "Appointment booked successfully!")
        return redirect('webpatient:patient_homepage')
    return render(request, 'patient/confirm_booking.html', {'token': token})



from django.shortcuts import render, redirect
from patient.models import tbl_appointment, tbl_patient

def myBookings(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')
    patient = tbl_patient.objects.get(id=patient_id)
    appointments = tbl_appointment.objects.filter(
        patient=patient,
        appointment_date__gte=date.today()   # today + future
    ).order_by('appointment_date', 'estimated_time')
    context = {
        'appointments': appointments
    }
    return render(request, 'patient/myBookings.html', context)



def generate_report(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')
    if request.method == 'POST':
        patient = tbl_patient.objects.get(id=patient_id)
        image_data = request.POST.get('image_data')
        disease = request.POST.get('disease')
        confidence = request.POST.get('confidence')
        
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
        messages.success(request, "Report generated successfully!")
        return redirect('webpatient:myReports')
        
    return redirect('webpatient:patient_homepage')



def myReports(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')
        
    patient = tbl_patient.objects.get(id=patient_id)
    reports = tbl_report.objects.filter(patient=patient).order_by('-report_date')
    
    context = {
        'reports': reports
    }
    return render(request, 'patient/myReports.html', context)





#Booking history
def appointment_history(request):
    pid = request.session['pid']   # logged patient id
    today = date.today()
    history = tbl_appointment.objects.filter(
        patient_id=pid,
        appointment_date__lt=today
    ).order_by('-appointment_date')
    return render(request, 'patient/history_booking.html', {'history': history})