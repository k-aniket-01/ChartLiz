from django.urls import path
from . import views

app_name = 'patterns'

urlpatterns = [
    path('api/markers/<str:symbol>/',      views.pattern_markers_api,           name='markers'),
    path('api/detail/<str:pattern_name>/', views.pattern_detail_api,            name='detail'),
    path('history/<str:symbol>/',          views.PatternHistoryView.as_view(),  name='history'),
]