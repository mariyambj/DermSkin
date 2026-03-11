from django.shortcuts import render,redirect,get_object_or_404
from clinicadmin.models import *
from .models import *
from datetime import datetime, timedelta, date


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


#edit profile
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




from datetime import datetime, timedelta, date
from django.shortcuts import render, redirect
from .models import tbl_doctor, tbl_schedule, tbl_slot


def doctor_schedule(request):

    doctor_id = request.session.get('did')
    doctor = tbl_doctor.objects.get(id=doctor_id)

    days = [
        ('mon','Monday'),
        ('tue','Tuesday'),
        ('wed','Wednesday'),
        ('thu','Thursday'),
        ('fri','Friday'),
        ('sat','Saturday')
    ]

    # already scheduled days
    scheduled_days = tbl_schedule.objects.filter(
        doctor=doctor
    ).values_list('day_of_week', flat=True)


    if request.method == 'POST':

        for key, day in days:

            if day in scheduled_days:
                continue

            available = True if request.POST.get(f'{key}_available') else False
            start = request.POST.get(f'{key}_start')
            end = request.POST.get(f'{key}_end')
            slot = request.POST.get(f'{key}_slot')
            break_start = request.POST.get(f'{key}_break_start')
            break_end = request.POST.get(f'{key}_break_end')

            if available and start and end:

                schedule = tbl_schedule.objects.create(
                    doctor=doctor,
                    day_of_week=day,
                    schedule_date=date.today(),
                    is_available=available,
                    start_time=start,
                    end_time=end,
                    slot_duration=slot,
                    break_start_time=break_start if break_start else None,
                    break_end_time=break_end if break_end else None
                )

                start_time = datetime.strptime(start,"%H:%M")
                end_time = datetime.strptime(end,"%H:%M")
                duration = int(slot)

                current = start_time

                while current < end_time:

                    slot_end = current + timedelta(minutes=duration)

                    if break_start and break_end:

                        bstart = datetime.strptime(break_start,"%H:%M")
                        bend = datetime.strptime(break_end,"%H:%M")

                        if current >= bstart and current < bend:
                            current = bend
                            continue

                    tbl_slot.objects.create(
                        doctor=doctor,
                        schedule=schedule,
                        day_of_week=day,
                        slot_start=current.time(),
                        slot_end=slot_end.time()
                    )

                    current = slot_end

        return redirect('webdoctor:doctor_schedule')


    # remove already scheduled days from form
    remaining_days = [d for d in days if d[1] not in scheduled_days]


    # get saved schedules
    saved_schedules = tbl_schedule.objects.filter(doctor=doctor)


    # attach slot count for each schedule
    schedule_data = []

    for schedule in saved_schedules:

        slot_count = tbl_slot.objects.filter(
            doctor=doctor,
            schedule=schedule
        ).count()

        schedule_data.append({
            "day": schedule.day_of_week,
            "start": schedule.start_time,
            "end": schedule.end_time,
            "duration": schedule.slot_duration,
            "slots": slot_count
        })


    return render(request,'doctor/schedule.html',{
        'days': remaining_days,
        'saved_schedules': schedule_data
    })


