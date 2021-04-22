from django.urls import path
from . import views

app_name = 'ups'

urlpatterns = [
    path('index/', views.show_index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/',views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('generics/', views.show_generic, name='generics'),
    path('track_package/', views.track_package, name='track_package'),
    #path('show_track_result/', views.show_track_result, name="show_track_result"),
    path('modify_destination_x/<int:package_id>', views.modify_destination_x, name='modify_destination_x'),
    path('modify_destination_y/<int:package_id>', views.modify_destination_y, name='modify_destination_y'),
    #path('modify_destination_y/', views.modify_destination_y, name="modify_destination_y"),
    path('see_packages/', views.see_packages, name='see_packages'),
    path('see_products/<int:package_id>', views.see_products, name='see_products'),
    path('send_message/', views.send_message, name='send_message'),
    path('elements/', views.show_elements, name='elements'),
]

