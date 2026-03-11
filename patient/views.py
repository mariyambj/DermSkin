from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from guest.models import *
from doctor.models import *
from clinicadmin.models import *
from .models import *
from datetime import datetime, timedelta, time




#homepage
def home_page(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('login')

    patient = tbl_patient.objects.get(id=patient_id)
    return render(request, 'patient/patient_homepage.html', {'patient': patient})


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


def book_appointment(request, doctor_id):
    doctor = get_object_or_404(tbl_doctor, id=doctor_id)

    # Get patient from session
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')
    try:
        patient = tbl_patient.objects.get(id=patient_id)
    except tbl_patient.DoesNotExist:
        return redirect('create_patient_profile')
    # Define default time slots (9 AM to 5 PM, 30 min each)
    
    default_start = time(9, 0)
    default_end = time(17, 0)
    slot_duration = timedelta(minutes=30)

    # Generate list of all slots
    slots = []
    current_time = datetime.combine(datetime.today(), default_start)
    end_datetime = datetime.combine(datetime.today(), default_end)
    while current_time < end_datetime:
        slot_str = f"{current_time.time().strftime('%H:%M')} to {(current_time + slot_duration).time().strftime('%H:%M')}"
        slots.append(slot_str)
        current_time += slot_duration

    if request.method == "POST":
        appointment_date = request.POST.get("appointment_date")
        time_slot = request.POST.get("time_slot")
        symptoms = request.POST.get("symptoms")

        if not time_slot:
            return render(request, "patient/booking_appointment.html", {
                "doctor": doctor,
                "time_slots": slots,
                "error": "Please select a time slot."
            })

        start_str, end_str = time_slot.split(" to ")
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()

        # Check if this doctor already has an appointment at the same time
        exists = tbl_appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            start_time=start_time
        ).exists()

        if exists:
            return render(request, "patient/booking_appointment.html", {
                "doctor": doctor,
                "time_slots": slots,
                "error": "This time slot is already booked. Please choose another."
            })

        # Create appointment
        tbl_appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            symptoms=symptoms,
            status="pending"
        )

        return redirect("appointment_success")  # redirect to a success page

    return render(request, "patient/booking_appointment.html", {
        "doctor": doctor,
        "time_slots": slots
    })