from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    path('',                    views.alert_list,           name='alert_list'),
    path('create/',             views.alert_create,         name='alert_create'),
    path('<int:pk>/delete/',    views.alert_delete,         name='alert_delete'),
    path('notifications/',      views.notification_center,  name='notification_center'),
    path('notifications/recent/',         views.recent_notifications, name='recent_notifications'),
    path('notifications/mark-all-read/',  views.mark_all_read,       name='mark_all_read'),
    path('notifications/<int:pk>/read/',  views.mark_read,           name='mark_read'),
]