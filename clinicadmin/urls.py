from django.urls import path
from clinicadmin import views
app_name='webadmin'

urlpatterns = [
    path('admin_homepage/', views.admin_homepage, name='admin_homepage'),
    path('doctor_registration/',views.doctor_registration,name='doctor_registration'),
    path('doctor_list/',views.doctor_list,name='doctor_list'),

]