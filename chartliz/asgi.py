import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import stocks.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chartliz.settings')

from stocks.routing import websocket_urlpatterns as stocks_ws
from alerts.routing import websocket_urlpatterns as alerts_ws

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            stocks_ws + alerts_ws
        )
    ),
})