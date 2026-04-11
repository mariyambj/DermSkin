import os
import django
import sqlite3

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smart_Derm.settings')
django.setup()

from clinicadmin.models import tbl_doctor

def insert_doctor():
    try:
        # We can also set a longer timeout for sqlite3 within Django by modifying DATABASES in settings,
        # but for a one-off script, we just try and catch.
        doctor = tbl_doctor.objects.create(
            name='Dr. John Smith',
            age=45,
            gender='Male',
            email='johnsmith@example.com',
            phone_number='+1234567890',
            address='123 Medical Plaza, City',
            specialization='Dermatology',
            qualification='MBBS, MD',
            medical_registration_number='REG123456',
            password='password123'
        )
        print(f"Doctor inserted successfully: {doctor.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    insert_doctor()
