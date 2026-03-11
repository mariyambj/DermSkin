from django.db import models
from clinicadmin.models import *
from guest.models import *
from .models import *

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
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    symptoms = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('doctor', 'appointment_date', 'start_time')
        constraints = [
            models.CheckConstraint(check=models.Q(end_time__gt=models.F('start_time')), name='end_time_after_start_time')
        ]
        ordering = ['appointment_date', 'start_time']

    def __str__(self):
        return f"{self.patient.username} with {self.doctor.name} on {self.appointment_date} at {self.start_time}"
