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

    SLOT_CHOICES = [
        (15, '15 minutes'),
        (20, '20 minutes'),
        (30, '30 minutes'),
        (45, '45 minutes'),
        (60, '60 minutes'),
    ]

    doctor = models.ForeignKey(tbl_doctor, on_delete=models.CASCADE)

    schedule_date = models.DateField()   # ⭐ NEW FIELD

    day_of_week = models.CharField(
        max_length=10,
        choices=DAY_CHOICES
    )

    is_available = models.BooleanField(default=True)

    start_time = models.TimeField()

    end_time = models.TimeField()

    slot_duration = models.IntegerField(
        choices=SLOT_CHOICES,
        default=30
    )

    break_start_time = models.TimeField(null=True, blank=True)
    break_end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.doctor.name} - {self.day_of_week}"
    
class tbl_slot(models.Model):

    doctor = models.ForeignKey(tbl_doctor, on_delete=models.CASCADE)

    schedule = models.ForeignKey(
        tbl_schedule,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    day_of_week = models.CharField(max_length=10)

    slot_start = models.TimeField()
    slot_end = models.TimeField()

    is_booked = models.BooleanField(default=False)
