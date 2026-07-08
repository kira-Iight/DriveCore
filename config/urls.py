# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="DriveCore API",
        default_version='v1',
        description="API для ИИ-ассистента платформенной занятости",
        contact=openapi.Contact(email="support@nexus.ru"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Главная страница с фронтендом
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/v1/', include('users.urls')),
    path('api/v1/chat/', include('chat.urls')),
    path('api/v1/taxes/', include('taxes.urls')),
    path('api/v1/docs/', include('docs.urls')),
    path('api/v1/news/', include('news.urls')),
    path('api/v1/analytics/', include('analytics.urls')),
    
    # Swagger/ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Для разработки - обслуживание статических и медиа файлов
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)