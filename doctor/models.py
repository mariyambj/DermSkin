from django.db import models
from clinicadmin.models import tbl_doctor


class tbl_schedule(models.Model):

    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]

    # Removed SLOT_CHOICES as they are no longer needed

    doctor = models.ForeignKey(tbl_doctor, on_delete=models.CASCADE)

    schedule_date = models.DateField()   # ⭐ NEW FIELD

    day_of_week = models.CharField(
        max_length=10,
        choices=DAY_CHOICES
    )

    is_available = models.BooleanField(default=True)

    start_time = models.TimeField()

    end_time = models.TimeField()

    # slot_duration removed in favor of total_patients token generation
    # consultation_duration added to automate token count calculation
    consultation_duration = models.IntegerField(default=15)

    total_patients = models.IntegerField(default=0)

    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.doctor.name} - {self.day_of_week}"
    

class tbl_token(models.Model):
    doctor = models.ForeignKey(tbl_doctor, on_delete=models.CASCADE)
    schedule = models.ForeignKey(tbl_schedule, on_delete=models.CASCADE, null=True, blank=True)
    
    date = models.DateField() # ⭐ ADDED: Makes querying by date much easier
    day_of_week = models.CharField(max_length=10)
    token_number = models.IntegerField()
    estimated_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        # Ensures a doctor cannot have duplicate token numbers on the same day
        unique_together = ('doctor', 'date', 'token_number')

    def __str__(self):
        return f"Token {self.token_number} - {self.doctor.name} on {self.date}"