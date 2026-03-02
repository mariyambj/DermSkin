from django.db import models

# Create your models here.
class tbl_patient(models.Model):

    GENDER_CHOICES =[
        ('M','Male'),
        ('F','Female'),
        ('O','Other'),
    ]
    first_name=models.CharField(max_length=20)
    address=models.TextField(blank=True)
    phone=models.CharField(max_length=20)
    email = models.EmailField(max_length=254)  # 254 is the default
    age=models.CharField(max_length=3)
    gender=models.CharField(max_length=1,choices=GENDER_CHOICES)
    pass_word=models.CharField(max_length=128) # 128 is standard for hashed passwords




