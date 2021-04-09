from django.urls import path
from . import views

app_name = 'ups'

urlpatterns = [
    path('index/', views.show_index, name="index"),
    path('login/', views.login, name='login'),
    path('generics/', views.show_generic, name="generics"),
    path('elements/', views.show_elements, name="elements"),
]