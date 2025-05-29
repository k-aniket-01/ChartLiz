"""
URL configuration for ChartLiz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ChartLiz import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/',views.user_login, name='login'),
    path('logout/',views.user_logout, name='logout'),
    path('save_prices/', views.save_prices, name='save_prices'),
    path('signup/', views.signup, name='signup'),
    path('market/',views.market, name='market'),
    path('portfolio/',views.portfolio, name='portfolio'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('contact/', views.contact, name='contact'),
    path('sell/', views.sell_view, name='sell'),
    path('about/', views.about, name='about'), 
    path('buy/', views.buy_view, name='buy_view'),
    path('contact/', views.contact, name='contact'),
    path('learn/',views.learn, name='learn'),
    path('api/crypto-data/', views.fetch_crypto_data, name='crypto-data'),
    path('charts/<str:coin_id>/', views.market, name='market_coin'),


]
