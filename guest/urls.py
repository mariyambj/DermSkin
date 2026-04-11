from django.urls import path
from guest import views 
app_name='webguest'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('upload/', views.upload_image, name='upload_image'),
    path('patient_list/',views.patient_list,name='patient_list'),
    path('home_page/',views.home_page,name='home_page'),
    path('', views.home_page),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('send_otp/', views.send_otp, name='send_otp'),
    path('verify_otp_forget/', views.verify_otp_forget, name='verify_otp_forget'),
    path('new_password/', views.new_password, name='new_password'),
]