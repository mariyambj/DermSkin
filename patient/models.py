from django.db import models
from clinicadmin.models import *
from guest.models import *
from .models import *
from doctor.models import *

# Create your models here.

class tbl_appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(tbl_patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(tbl_doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    token_number = models.IntegerField()
    estimated_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    symptoms = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('doctor', 'appointment_date', 'token_number')
        ordering = ['appointment_date', 'token_number']

    def __str__(self):
        return f"{self.patient.username} with {self.doctor.name} on {self.appointment_date} (Token {self.token_number})"

class tbl_report(models.Model):
    patient = models.ForeignKey(tbl_patient, on_delete=models.CASCADE, related_name='reports')
    disease = models.CharField(max_length=200)
    confidence = models.CharField(max_length=50)
    image = models.ImageField(upload_to='patient_reports/')
    report_date = models.DateTimeField(auto_now_add=True)
    appointment = models.ForeignKey(tbl_appointment,on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return f"Report - {self.patient.first_name} - {self.disease}"


class tbl_feedback(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    patient     = models.ForeignKey(tbl_patient, on_delete=models.CASCADE, related_name='feedbacks')
    doctor      = models.ForeignKey(tbl_doctor, on_delete=models.CASCADE, related_name='feedbacks')
    appointment = models.OneToOneField(tbl_appointment, on_delete=models.CASCADE, related_name='feedback')
    rating      = models.IntegerField(choices=RATING_CHOICES)
    comment     = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.first_name} → {self.doctor.name} ({self.rating}★)"