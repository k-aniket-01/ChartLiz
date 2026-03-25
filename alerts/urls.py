from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('',                    views.alert_list,   name='alert_list'),
    path('create/',             views.alert_create, name='alert_create'),
    path('<int:pk>/delete/',    views.alert_delete, name='alert_delete'),
]