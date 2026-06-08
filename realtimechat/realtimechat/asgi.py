"""
ASGI config for realtimechat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
 
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realtimechat.settings")
 
# Initialise Django before importing anything that touches models
django_asgi_app = get_asgi_application()
 
from chat.routing import websocket_urlpatterns  # noqa: E402
 
application = ProtocolTypeRouter({
    # All standard HTTP requests go to Django as normal
    "http": django_asgi_app,
 
    # WebSocket connections are authenticated via the Django session cookie,
    # then routed to the correct consumer by slug
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
 