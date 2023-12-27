"""
ASGI config for advising_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advising_project.settings')

application = get_asgi_application()

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from advising_app import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'advising_project.settings')

# Initialize Django ASGI application early to ensure the AppRegistry is populated
# before importing the consumers module.
django_asgi_app = get_asgi_application()

# Define websocket urlpattern
websocket_urlpatterns = [
    path('ws/chat/<str:room_name>/', consumers.ChatConsumer.as_asgi()),
]

# Define the ASGI application
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Define the Channels HTTP application
    "websocket": AuthMiddlewareStack(  # Enable Django's session auth for WebSockets
        URLRouter(
            websocket_urlpatterns  # Point to the routing of your WebSocket consumers
        )
    ),
})
