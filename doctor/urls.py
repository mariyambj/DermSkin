from django.urls import path
from doctor import views
app_name='webdoctor'


urlpatterns = [
   path('doctor_homepage/', views.doctor_homepage, name='doctor_homepage'),
   path('doctor_profile/',views.doctor_profile,name='doctor_profile'),
   path('doctor_editprofile/',views.doctor_editprofile,name='doctor_editprofile'),
   path('doctor_changepassword/',views.doctor_changepassword,name='doctor_changepassword'),
   path('doctor_schedule/',views.doctor_schedule,name='doctor_schedule'),
  

]