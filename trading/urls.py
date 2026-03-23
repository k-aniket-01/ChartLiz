from django.urls import path
from . import views

app_name = 'trading'

urlpatterns = [
    path('order/',      views.place_market_order,   name='place_order'),
    path('dashboard/',  views.portfolio_dashboard,  name= 'dashboard'),
]