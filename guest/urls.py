from django.urls import path
from guest import views 
app_name='webguest'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('upload/', views.upload_image, name='upload_image'),
    path('patient_list/',views.patient_list,name='patient_list'),

]