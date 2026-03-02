from django.urls import path
from . import views

urlpatterns = [
   path('patient_homepage/', views.home_page, name='patient_homepage'),
   path('patient_profile/',views.patient_profile,name='patient_profile'),
   path('edit_profile/',views.edit_profile,name='edit_profile'),
   path('change_passwsord/',views.change_password,name='change_password'),

]