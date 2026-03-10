from django.shortcuts import render,redirect,get_object_or_404
from clinicadmin.models import *

# Create your views here.


def doctor_homepage(request):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('doctor_login')
    return render(request, 'doctor/doctor_homepage.html')


def doctor_profile(request):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('login')
    doctor = get_object_or_404(tbl_doctor, id=doctor_id)
    return render(request, 'doctor/doctor_profile.html', {'doctor': doctor})





def doctor_editprofile(request):
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





