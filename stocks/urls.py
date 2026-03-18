from django.urls import path
from . import views


urlpatterns = [
    path('search/', views.stock_search, name='stock_search'),
    path('search/api/',views.stock_search_api, name='stock_search_api'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('market/status/', views.market_status, name='market_status'),
    path('stock/<str:symbol>/ohlcv/',views.stock_ohlcv, name='stock_ohlcv'),
    path('<str:symbol>/', views.stock_detail, name='stock_detail'),
    path('<str:symbol>/api/ohlcv/', views.ohlcv_api, name='ohlcv_api'),
    path('<str:symbol>/watchlist/',views.toggle_watchlist, name='toggle_watchlist'),
    
]