import os
import django
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chartliz.settings')

django.setup()

import stocks.routing
import alerts.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            stocks.routing.websocket_urlpatterns +
            alerts.routing.websocket_urlpatterns
        )
    ),
})