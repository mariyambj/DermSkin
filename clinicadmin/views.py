from django.contrib import messages
from django.shortcuts import render, redirect
from clinicadmin.models import *

def admin_homepage(request):
    return render(request, 'clinicadmin/admin_homepage.html')


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
                profile_picture=request.FILES.get('profile_picture'),
                identification=request.FILES.get('identification_proof')
            )
            messages.success(request, "Doctor registered successfully!")
        return redirect('webadmin:doctor_registration')
    return render(request, 'clinicadmin/doctor_registration.html', {
        'specializations': SPECIALIZATION_CHOICES
    })


def doctor_list(request):
    doctors = tbl_doctor.objects.all()
    return render(request,'clinicadmin/doctor_list.html',{'doctors':doctors})