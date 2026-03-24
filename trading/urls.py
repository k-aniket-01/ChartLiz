from django.urls import path
from . import views

app_name = 'trading'

urlpatterns = [
    path('order/',                          views.place_market_order,   name='place_order'),
    path('order/limit/',                    views.place_limit_order,    name='place_limit_order'),
    path('order/stop/',                     views.place_stop_order,     name='place_stop_order'),
    path('order/cancel/<int:order_id>/',    views.cancel_limit_order,   name='cancel_order'),
    path('dashboard/',                      views.portfolio_dashboard,  name='dashboard'),
    path('pnl-history/',                    views.pnl_history_json,     name='pnl_history'),
    path('history/',                        views.trade_history,        name='trade_history'),

]