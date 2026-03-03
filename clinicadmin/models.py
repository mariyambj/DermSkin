from django.db import models

# Create your models here.


class tbl_admin(models.Model):
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=128)


class tbl_doctor(models.Model):
    name=models.CharField(max_length=20)
    age=models.IntegerField()
    gender=models.CharField(max_length=10)
    profile_picture=models.ImageField(upload_to='doctor_profiles/', blank=True, null=True)
    email=models.EmailField(max_length=128,unique=True)
    phone_number=models.CharField(max_length=20)
    address=models.TextField()
    identification=models.ImageField(upload_to='doctor_id_proofs/', blank=True, null=True)
    specialization=models.CharField(max_length=30)
    qualification = models.CharField(max_length=50, blank=True, null=True)
    medical_registration_number=models.CharField(max_length=20,unique=True)

    
