from django.shortcuts import render,redirect
from guest.models import *


#homepage
def home_page(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login')

    patient = tbl_patient.objects.get(id=patient_id)
    return render(request, 'patient/patient_homepage.html', {'patient': patient})


#Patient Profile

def patient_profile(request):
    patient_id=request.session.get('patient_id')
    if not patient_id:
        return redirect('login')
    patient=tbl_patient.objects.get(id=patient_id)
    return render(request,'patient/patient_profile.html',{'patient':patient})


def edit_profile(request):
    patient_id=request.session.get('patient_id')
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
    patient_id=request.session.get('patient_id')
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