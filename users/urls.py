from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
]