from django.shortcuts import render,redirect,get_object_or_404
from clinicadmin.models import *
from .models import *
from datetime import datetime, timedelta, date


# Create your views here.


# doctor/views.py
def doctor_homepage(request):
    doctor_id = request.session.get('did')
    if not doctor_id:
        return redirect('webguest:login')
    
    doctor = get_object_or_404(tbl_doctor, id=doctor_id)
    today = date.today()
    
    # Fetch today's appointments
    from patient.models import tbl_appointment
    todays_appointments = tbl_appointment.objects.filter(
        doctor=doctor, 
        appointment_date=today
    ).order_by('estimated_time')

    # Stats
    context = {
        'doctor': doctor,
        'todays_count': todays_appointments.count(),
        'pending_reports': 5, # Placeholder
        'avg_time': 15,        # Placeholder
        'monthly_earnings': 12500, # Placeholder
        'appointments': todays_appointments,
        'recent_patients': tbl_appointment.objects.filter(doctor=doctor).order_by('-appointment_date')[:5],
        'profile_progress': 85
    }
    return render(request, 'doctor/home.html', context)


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



# doctor/views.py
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import tbl_schedule, tbl_token
from clinicadmin.models import tbl_doctor



from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, timedelta
from .models import tbl_schedule, tbl_token
from clinicadmin.models import tbl_doctor

def doctor_schedule(request):
    # 1. Get ID from session and verify the doctor exists FIRST
    doctor_id = request.session['did']
    
    if not doctor_id:
        messages.error(request, "You must be logged in to access this page.")
        return redirect('webguest:login')  # Update 'login' if your login URL name is different
        
    try:
        doctor = tbl_doctor.objects.get(id=doctor_id)
    except tbl_doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('webguest:login')

    # 2. Handle the Form Submission
    if request.method == 'POST':
        schedule_date = request.POST.get('schedule_date')
        day_of_week = request.POST.get('day_of_week')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        break_start_str = request.POST.get('break_start_time')
        break_end_str = request.POST.get('break_end_time')
        consultation_duration = int(request.POST.get('consultation_duration'))
        total_patients = int(request.POST.get('total_patients'))

        # Save the main Schedule record using the 'doctor' variable we securely fetched above
        schedule = tbl_schedule.objects.create(
            doctor=doctor,
            schedule_date=schedule_date,
            day_of_week=day_of_week,
            start_time=start_time_str,
            end_time=end_time_str,
            consultation_duration=consultation_duration,
            total_patients=total_patients,
            break_start_time=break_start_str if break_start_str else None,
            break_end_time=break_end_str if break_end_str else None
        )

        # Time Calculations for Tokens
        fmt = '%H:%M'
        current_time = datetime.strptime(start_time_str, fmt)
        break_start = datetime.strptime(break_start_str, fmt) if break_start_str else None
        break_end = datetime.strptime(break_end_str, fmt) if break_end_str else None

        # Generate Tokens Loop
        for i in range(1, total_patients + 1):
            # Fast-forward past the break time if we hit it
            if break_start and break_end and break_start <= current_time < break_end:
                current_time = break_end

            # Create the Token
            tbl_token.objects.create(
                doctor=doctor,
                schedule=schedule,
                date=schedule_date,
                day_of_week=day_of_week,
                token_number=i,
                estimated_time=current_time.time(),
                is_booked=False
            )
            
            # Increment time for the next token
            current_time += timedelta(minutes=consultation_duration)

        messages.success(request, f"Schedule saved! {total_patients} tokens successfully generated.")
        return redirect('webdoctor:doctor_schedule') # Redirects back to clear the form

    # 3. If GET request, just render the page
    return render(request, 'doctor/schedule.html')
    # 1. Get the logged-in doctor from the session
    doctor_id = request.session['did']# Check your login view to see if this matches your session key!
    
    if not doctor_id:
        messages.error(request, "You must be logged in to set a schedule.")
        return redirect('webguest:login') # Change this to your actual login URL name
        
   

    if request.method == 'POST':
        # 2. Fetch data from POST request
        schedule_date = request.POST.get('schedule_date')
        day_of_week = request.POST.get('day_of_week')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        break_start_str = request.POST.get('break_start_time')
        break_end_str = request.POST.get('break_end_time')
        consultation_duration = int(request.POST.get('consultation_duration'))
        total_patients = int(request.POST.get('total_patients'))

        # 3. Save the main Schedule record
        schedule = tbl_schedule.objects.create(
            doctor=doctor,
            schedule_date=schedule_date,
            day_of_week=day_of_week,
            start_time=start_time_str,
            end_time=end_time_str,
            consultation_duration=consultation_duration,
            total_patients=total_patients,
            break_start_time=break_start_str if break_start_str else None,
            break_end_time=break_end_str if break_end_str else None
        )

        # 4. Time Calculations for Tokens
        fmt = '%H:%M'
        current_time = datetime.strptime(start_time_str, fmt)
        
        break_start = datetime.strptime(break_start_str, fmt) if break_start_str else None
        break_end = datetime.strptime(break_end_str, fmt) if break_end_str else None

        # 5. Generate Tokens Loop
        for i in range(1, total_patients + 1):
            # If the current estimated time hits the break, fast-forward to break end
            if break_start and break_end and break_start <= current_time < break_end:
                current_time = break_end

            # Create the Token
            tbl_token.objects.create(
                doctor=doctor,
                schedule=schedule,
                date=schedule_date,
                day_of_week=day_of_week,
                token_number=i,
                estimated_time=current_time.time(),
                is_booked=False
            )
            
            # Increment time for the next token by the consultation duration
            current_time += timedelta(minutes=consultation_duration)

        messages.success(request, f"Schedule saved and {total_patients} tokens generated!")
        return redirect('doctor_schedule') # Redirect back to the form or dashboard

    return render(request, 'doctor/schedule.html')
    if request.method == 'POST':
        # 1. Fetch data from POST request
        doctor = request.user.doctor # Assuming the logged-in user is linked to tbl_doctor
        schedule_date = request.POST.get('schedule_date')
        day_of_week = request.POST.get('day_of_week')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        break_start_str = request.POST.get('break_start_time')
        break_end_str = request.POST.get('break_end_time')
        consultation_duration = int(request.POST.get('consultation_duration'))
        total_patients = int(request.POST.get('total_patients'))

        # 2. Save the main Schedule record
        schedule = tbl_schedule.objects.create(
            doctor=doctor,
            schedule_date=schedule_date,
            day_of_week=day_of_week,
            start_time=start_time_str,
            end_time=end_time_str,
            consultation_duration=consultation_duration,
            total_patients=total_patients,
            break_start_time=break_start_str if break_start_str else None,
            break_end_time=break_end_str if break_end_str else None
        )

        # 3. Time Calculations for Tokens
        fmt = '%H:%M'
        current_time = datetime.strptime(start_time_str, fmt)
        
        break_start = datetime.strptime(break_start_str, fmt) if break_start_str else None
        break_end = datetime.strptime(break_end_str, fmt) if break_end_str else None

        # 4. Generate Tokens Loop
        for i in range(1, total_patients + 1):
            # If the current estimated time hits the break, fast-forward to break end
            if break_start and break_end and break_start <= current_time < break_end:
                current_time = break_end

            # Create the Token
            tbl_token.objects.create(
                doctor=doctor,
                schedule=schedule,
                date=schedule_date,
                day_of_week=day_of_week,
                token_number=i,
                estimated_time=current_time.time(),
                is_booked=False
            )
            
            # Increment time for the next token by the consultation duration
            current_time += timedelta(minutes=consultation_duration)

        messages.success(request, f"Schedule saved and {total_patients} tokens generated!")
        return redirect('doctor_dashboard')

    return render(request, 'doctor/schedule.html')

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
            duration = request.POST.get(f'{key}_duration') # New: average time per patient
            break_start = request.POST.get(f'{key}_break_start')
            break_end = request.POST.get(f'{key}_break_end')
            schedule_date = request.POST.get(f'{key}_date')

            if available and start and end and duration and int(duration) > 0 and schedule_date:
                # Calculate total patients based on duration
                start_dt = datetime.combine(date.today(), datetime.strptime(start, '%H:%M').time())
                end_dt = datetime.combine(date.today(), datetime.strptime(end, '%H:%M').time())
                
                if end_dt <= start_dt:
                    end_dt += timedelta(days=1)
                
                total_minutes = (end_dt - start_dt).total_seconds() / 60
                
                # Subtract break duration if applicable
                if break_start and break_end:
                    b_start_dt = datetime.combine(date.today(), datetime.strptime(break_start, '%H:%M').time())
                    b_end_dt = datetime.combine(date.today(), datetime.strptime(break_end, '%H:%M').time())
                    if b_end_dt <= b_start_dt:
                        b_end_dt += timedelta(days=1)
                    break_minutes = (b_end_dt - b_start_dt).total_seconds() / 60
                    total_minutes -= break_minutes

                calculated_total_patients = int(total_minutes // int(duration))

                schedule = tbl_schedule.objects.create(
                    doctor=doctor,
                    day_of_week=day,
                    schedule_date=schedule_date,
                    is_available=available,
                    start_time=start,
                    end_time=end,
                    consultation_duration=duration,
                    total_patients=calculated_total_patients,
                    break_start_time=break_start if break_start else None,
                    break_end_time=break_end if break_end else None
                )

                current_time = start_time

                for i in range(1, total_patients + 1):
                    
                    # If current time falls within the break, skip to the end of the break
                    if break_start and break_end:
                        if bstart <= current_time < bend:
                            current_time = bend

                    tbl_token.objects.create(
                        doctor=doctor,
                        schedule=schedule,
                        day_of_week=day,
                        token_number=i,
                        estimated_time=current_time.time()
                    )
                    
                    # Advance time by the calculated gap
                    current_time += timedelta(minutes=gap_minutes)

        return redirect('webdoctor:doctor_schedule')


    # remove already scheduled days from form
    remaining_days = [d for d in days if d[1] not in scheduled_days]


    # get saved schedules
    saved_schedules = tbl_schedule.objects.filter(doctor=doctor)


    # attach token count for each schedule
    schedule_data = []

    for schedule in saved_schedules:

        token_count = tbl_token.objects.filter(
            doctor=doctor,
            schedule=schedule
        ).count()

        schedule_data.append({
            "day": schedule.day_of_week,
            "date": schedule.schedule_date,
            "start": schedule.start_time,
            "end": schedule.end_time,
            "total_patients": schedule.total_patients,
            "tokens": token_count
        })


    return render(request,'doctor/schedule.html',{
        'days': remaining_days,
        'saved_schedules': schedule_data
    })


