# config/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from chat.consumers import ChatConsumer

# Получаем ASGI приложение Django
django_asgi_app = get_asgi_application()

# Обертываем для обработки статики
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

application = ProtocolTypeRouter({
    'http': ASGIStaticFilesHandler(django_asgi_app),  # ← Добавляем поддержку статики
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws/chat/<int:user_id>/', ChatConsumer.as_asgi()),
        ])
    ),
})
