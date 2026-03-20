from django.urls import path
from . import views

app_name = 'patterns'    # ← this must be here

urlpatterns = [
    path('api/markers/<str:symbol>/', views.pattern_markers_api, name='markers'),
    path('history/<str:symbol>/', views.PatternHistoryView.as_view(), name='history'),
]