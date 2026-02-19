from django.urls import path
from . import views 

urlpatterns = [
    path('login/', views.login, name='login'),
    path('registration/', views.registration, name='registration'),
    path('upload/', views.upload_image, name='upload_image'),
]