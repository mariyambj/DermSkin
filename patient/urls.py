from django.urls import path
from . import views
app_name='webpatient'

urlpatterns = [
   path('patient_homepage/', views.home_page, name='patient_homepage'),
   path('patient_profile/',views.patient_profile,name='patient_profile'),
   path('edit_profile/',views.edit_profile,name='edit_profile'),
   path('change_passwsord/',views.change_password,name='change_password'),
   path('doctor_list/',views.doctor_list,name='doctor_list'),
   path('doctor_details/<int:id>/', views.doctor_details, name='doctor_details'),
   path('book_appointment/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
   path('confirm_booking/<int:token_id>/', views.confirm_booking, name='confirm_booking'),
   path('myBookings/',views.myBookings, name='myBookings'),
   
]