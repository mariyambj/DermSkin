from django.urls import path
from clinicadmin import views
app_name='webadmin'

urlpatterns = [
    path('admin_homepage/', views.admin_homepage, name='admin_homepage'),
    path('doctor_registration/',views.doctor_registration,name='doctor_registration'),
    path('admin_doctor_list/',views.admin_doctor_list,name='admin_doctor_list'),
    path('delete_doctor/<int:id>/',views.delete_doctor,name='delete_doctor'),

]