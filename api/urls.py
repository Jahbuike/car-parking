from django.urls import path
from . import views

urlpatterns = [
    path('', views.parking_entry_view, name='parking_entry'),
    path('checkout/<int:pk>/', views.checkout_driver, name='checkout_driver'),
    path('daily-reset/', views.daily_reset, name='daily_reset'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('', views.parking_entry_view, name='parking_entry'),
    path('api/get-driver/', views.get_driver_details, name='get_driver_details'),
    path('api/get-tallies/', views.get_available_tallies, name='get_available_tallies'),
]