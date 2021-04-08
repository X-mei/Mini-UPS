from django.urls import path
from . import views

app_name = 'ups'

urlpatterns = [
    path('index/', views.show_index, name="index"),
]