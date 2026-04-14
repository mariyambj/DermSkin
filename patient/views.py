from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from guest.models import *
from doctor.models import *
from clinicadmin.models import *
from .models import *
from datetime import datetime, timedelta, time, date
import base64
from django.core.files.base import ContentFile
from django.db.models import Q
from datetime import date



#homepage
'''def home_page(request):
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
    return render(request, 'patient/home.html', context)'''

def home_page(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')
    patient = tbl_patient.objects.get(id=patient_id)
    appointments = tbl_appointment.objects.filter(patient=patient)
    query = request.GET.get('q')
    department = request.GET.get('department')
    doctors = tbl_doctor.objects.all()
    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(qualification__icontains=query)
        )
    if department and department != "All":
        doctors = doctors.filter(specialization__icontains=department)
    context = {
        'patient': patient,
        'total_appointments': appointments.count(),
        'upcoming_appointments': appointments.filter(
            appointment_date__gte=date.today(),
            status='confirmed'
        ).count(),
        'prescriptions': 2,
        'reports_ready': 1,
        'recent_appointments': appointments.order_by('-appointment_date')[:5],
        'doctors': doctors,
        'query': query,
        'department': department
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

from django.db.models import Q

def doctor_list(request):
    query = request.GET.get('q')
    doctors = tbl_doctor.objects.all()
    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(qualification__icontains=query)
        )
    return render(request, 'patient/doctor_list.html', {
        'doctors': doctors,
        'query': query
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
    tokens = None   # ❗ No tokens initially
    if selected_date:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
        # ❌ Prevent past booking
        if selected_date < date.today():
            messages.error(request, "You cannot book past dates.")
            return redirect('webpatient:book_appointment', doctor_id=doctor_id)
        # ✔ Check doctor schedule
        schedule = tbl_schedule.objects.filter(
            doctor=doctor,
            schedule_date=selected_date,
            is_available=True
        ).first()
        if not schedule:
            messages.error(request, "Doctor is not available on this date.")
        else:
            # ✔ Fetch tokens only if schedule exists
            tokens = tbl_token.objects.filter(
                doctor=doctor,
                date=selected_date
            ).order_by('token_number')
    context = {
        'doctor': doctor,
        'tokens': tokens,
        'selected_date': selected_date,
        'today': date.today()
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
        appointment = tbl_appointment.objects.create(
            patient=patient,
            doctor=token.doctor,
            appointment_date=token.date,
            token_number=token.token_number,
            estimated_time=token.estimated_time,
            symptoms=symptoms,
        )
    # force status update properly
        appointment.status = "confirmed"
        appointment.save()
        token.is_booked = True
        token.save()
        messages.success(request, "Appointment booked successfully!")
        return redirect('webpatient:patient_homepage')
    return render(request, 'patient/confirm_booking.html', {'token': token})



from django.shortcuts import render, redirect
from patient.models import tbl_appointment, tbl_patient

'''def myBookings(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')
    patient = tbl_patient.objects.get(id=patient_id)
    appointments = tbl_appointment.objects.filter(
        patient=patient,
        appointment_date__gte=date.today()
    ).exclude(status="cancelled").order_by('appointment_date', 'estimated_time')
    context = {
        'appointments': appointments
    }
    return render(request, 'patient/myBookings.html', context) '''



def myBookings(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')
    patient = tbl_patient.objects.get(id=patient_id)
    # Upcoming = pending/confirmed 
    appointments = tbl_appointment.objects.filter(
        patient=patient,
        appointment_date__gte=date.today()
    ).exclude(status__in=["cancelled"]).order_by('appointment_date', 'estimated_time')
    # Get appointment IDs that already have feedback submitted
    from patient.models import tbl_feedback
    feedbacked_ids = set(
        tbl_feedback.objects.filter(patient=patient).values_list('appointment_id', flat=True)
    )
    context = {
        'appointments': appointments,
        'feedbacked_ids': feedbacked_ids,
    }
    return render(request, 'patient/myBookings.html', context)



#feedback
def submit_feedback(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')
    if request.method == 'POST':
        from patient.models import tbl_feedback, tbl_appointment
        appointment_id = request.POST.get('appointment_id')
        rating         = request.POST.get('rating')
        comment        = request.POST.get('comment', '').strip()
        appointment = get_object_or_404(tbl_appointment, id=appointment_id, patient_id=patient_id)
        # Guard: only allow feedback on completed appointments
        if appointment.status != 'completed':
            messages.error(request, "Feedback can only be submitted for completed appointments.")
            return redirect('webpatient:myBookings')
        # Guard: prevent duplicate feedback
        if tbl_feedback.objects.filter(appointment=appointment).exists():
            messages.warning(request, "You have already submitted feedback for this appointment.")
            return redirect('webpatient:myBookings')
        tbl_feedback.objects.create(
            patient=appointment.patient,
            doctor=appointment.doctor,
            appointment=appointment,
            rating=rating,
            comment=comment or None,
        )
        messages.success(request, "Thank you! Your feedback has been submitted.")
    return redirect('webpatient:myBookings')



#cancel appointment
def cancel_appointment(request, app_id):
    if request.method == 'POST':
        appointment = get_object_or_404(tbl_appointment, id=app_id)
        appointment.status = "cancelled"
        appointment.save()
        messages.success(request, "Appointment cancelled successfully.")
    return redirect('webpatient:myBookings')


#generate report
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



#Reports
def myReports(request):
    patient_id = request.session.get('pid')
    if not patient_id:
        return redirect('webguest:login')
    patient = tbl_patient.objects.get(id=patient_id)
    # Pass ALL reports — template handles show/hide
    reports = tbl_report.objects.filter(patient=patient).order_by('-report_date')
    context = {
        'reports': reports
    }
    return render(request, 'patient/myReports.html', context)




#Booking history
'''from django.db.models import Q
def appointment_history(request):
    pid = request.session['pid']
    today = date.today()
    history = tbl_appointment.objects.filter(
        patient_id=pid
    ).filter(
        Q(appointment_date__lt=today) | Q(status__iexact="cancelled")
    ).order_by('-appointment_date')
    return render(request, 'patient/history_booking.html', {'history': history})'''


#Booking history
def appointment_history(request):
    pid = request.session['pid']
    today = date.today()
    history = tbl_appointment.objects.filter(
        patient_id=pid,
        appointment_date__lt=today
    ).filter(
        status__in=["confirmed", "cancelled","Cancelled","Completed","completed"]   # explicitly include both
    ).order_by('-appointment_date')
    return render(request, 'patient/history_booking.html', {'history': history})



from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .models import tbl_report

def download_report_pdf(request, rid):
    # Fetch the report object
    report = tbl_report.objects.get(id=rid)
    
    # Create the HTTP response with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{rid}.pdf"'
    
    # Initialize the document
    doc = SimpleDocTemplate(
        response, 
        pagesize=letter, 
        rightMargin=50, 
        leftMargin=50, 
        topMargin=50, 
        bottomMargin=50
    )
    styles = getSampleStyleSheet()
    elements = []

    # Define professional styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor("#2C3E50"),
        alignment=1,  # Center alignment
        spaceAfter=20
    )

    # 1. Add Title [cite: 1]
    elements.append(Paragraph("SmartDerm Analysis Report", title_style))
    elements.append(Spacer(1, 15))

    # 2. Logic for Doctor Name 
    doctor_name = "Not Assigned"
    if report.appointment and report.appointment.doctor:
        doctor_name = report.appointment.doctor.name

    # 3. Data Table for standardized layout [cite: 2, 3, 4]
    data = [
        ["Disease Detected:", f"{report.disease}"],
        ["Confidence Level:", f"{report.confidence}%"],
        ["Report Date:", f"{report.report_date}"],
        ["Doctor Name:", f"{doctor_name}"],
    ]

    table = Table(data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#34495E")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.lightgrey),
    ]))
    elements.append(table)

    # 4. Branding Footer [cite: 6]
    elements.append(Spacer(1, 40))
    footer_style = ParagraphStyle(
        'Footer', 
        parent=styles['Italic'], 
        fontSize=9, 
        alignment=1, 
        textColor=colors.grey
    )
    elements.append(Paragraph("Generated by SmartDerm Deeplearning Dermatology Assistant", footer_style))

    # Build and return the PDF
    doc.build(elements)
    return response