from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('patterns/',         views.pattern_list,   name='pattern_list'),
    path('patterns/<slug:slug>/', views.pattern_detail, name='pattern_detail'),
]