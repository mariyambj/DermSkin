from django.urls import path
from doctor import views
app_name='webdoctor'


urlpatterns = [
   path('doctor_homepage/', views.doctor_homepage, name='doctor_homepage'),
   path('doctor_profile/',views.doctor_profile,name='doctor_profile'),
   path('doctor_editprofile/',views.doctor_editprofile,name='doctor_editprofile'),
   path('doctor_changepassword/',views.doctor_changepassword,name='doctor_changepassword'),
   path('doctor_schedule/',views.doctor_schedule,name='doctor_schedule'),
   path('doctor_view_schedule/',views.doctor_view_schedule,name='doctor_view_schedule'),
   path('delete_schedule/<int:id>/',views.delete_schedule,name='delete_schedule'),
   path('doctor_patient_bookings/',views.doctor_patient_bookings,name='doctor_patient_bookings'),
   path('patient_details/<int:id>/',views.patient_details,name='patient_details'),
   path('update_booking_status/<int:appointment_id>/<str:status>/',views.update_booking_status,name='update_booking_status'),
   path('doctor_reports/',views.doctor_reports,name='doctor_reports'),
]