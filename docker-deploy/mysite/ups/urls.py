from django.urls import path
from . import views

app_name = 'ups'

urlpatterns = [
    path('index/', views.show_index, name="index"),
    path('login/', views.user_login, name='login'),
    path('logout/',views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('generics/', views.show_generic, name="generics"),
    path('elements/', views.show_elements, name="elements"),
]