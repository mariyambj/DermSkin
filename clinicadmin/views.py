from django.contrib import messages
from django.shortcuts import render, redirect
from clinicadmin.models import *
from django.shortcuts import redirect, get_object_or_404
from patient.models import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

def admin_homepage(request):
    patient_count=tbl_patient.objects.count()
    doctor_count=tbl_doctor.objects.count()
    return render(request, 'clinicadmin/admin_homepage.html',{'doctor_count':doctor_count,'patient_count':patient_count})


'''def doctor_registration(request):
    SPECIALIZATION_CHOICES = [
        ('Dermatology', 'Dermatology'),
        ('Cosmetology', 'Cosmetology'),
        ('Dermato Surgery', 'Dermato Surgery'),
        ('Trichology', 'Trichology (Hair Specialist)'),
        ('Pediatric Dermatology', 'Pediatric Dermatology'),
        ('Aesthetic Dermatology', 'Aesthetic Dermatology'),
    ]
    if request.method == 'POST':
        reg_no = request.POST['medical_registration_number']
        # Check if doctor already exists
        if tbl_doctor.objects.filter(medical_registration_number=reg_no).exists():
            messages.error(request, "Doctor already registered with this Medical Registration Number.")
        else:
            tbl_doctor.objects.create(
                name=request.POST['name'],
                age=request.POST['age'],
                gender=request.POST['gender'],
                email=request.POST['email'],
                phone_number=request.POST['phone_number'],
                address=request.POST['address'],
                specialization=request.POST['specialization'],
                qualification=request.POST['qualification'],
                medical_registration_number=reg_no,
                password=request.POST['password'],
                profile_picture=request.FILES.get('profile_picture'),
                identification=request.FILES.get('identification_proof')
            )
            messages.success(request, "Doctor registered successfully!")
        return redirect('webadmin:doctor_registration')
    return render(request, 'clinicadmin/doctor_registration.html', {
        'specializations': SPECIALIZATION_CHOICES
    })'''

#doctor registration
def doctor_registration(request):

    SPECIALIZATION_CHOICES = [
        ('Dermatology', 'Dermatology'),
        ('Cosmetology', 'Cosmetology'),
        ('Dermato Surgery', 'Dermato Surgery'),
        ('Trichology', 'Trichology (Hair Specialist)'),
        ('Pediatric Dermatology', 'Pediatric Dermatology'),
        ('Aesthetic Dermatology', 'Aesthetic Dermatology'),
    ]
    if request.method == 'POST':
        reg_no = request.POST['medical_registration_number']
        email = request.POST['email']
        password = request.POST['password']
        # Check if doctor already exists
        if tbl_doctor.objects.filter(medical_registration_number=reg_no).exists():
            messages.error(request, "Doctor already registered with this Medical Registration Number.")
        else:
            doctor = tbl_doctor.objects.create(
                name=request.POST['name'],
                age=request.POST['age'],
                gender=request.POST['gender'],
                email=email,
                phone_number=request.POST['phone_number'],
                address=request.POST['address'],
                specialization=request.POST['specialization'],
                qualification=request.POST['qualification'],
                medical_registration_number=reg_no,
                password=password,
                profile_picture=request.FILES.get('profile_picture'),
                identification=request.FILES.get('identification_proof')
            )
            # Send email to doctor
            subject = "Doctor Account Created"
            message = f"""
Hello {doctor.name},
Your account has been created successfully in the Smart Derm Clinic System.
Login Details:

Email: {email}
Password: {password}

Please login and change your password after first login.

Thank You.
SmartDerm Clinic
"""

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Doctor registered successfully and login details sent to email!")

        return redirect('webadmin:doctor_registration')

    return render(request, 'clinicadmin/doctor_registration.html', {
        'specializations': SPECIALIZATION_CHOICES
    })


#doctor list
def admin_doctor_list(request):
    doctors = tbl_doctor.objects.all()
    return render(request,'clinicadmin/doctor_list.html',{'doctors':doctors})

def delete_doctor(request,id):
    doctor = get_object_or_404(tbl_doctor, id=id)
    doctor.delete()
    return redirect('webadmin:admin_doctor_list')