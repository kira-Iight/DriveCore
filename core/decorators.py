"""
Декораторы для кэширования и валидации
"""
from functools import wraps
from django.core.cache import cache
from rest_framework.response import Response
import hashlib
import time


def cache_response(timeout=3600, key_prefix='', user_based=True):
    """
    Декоратор для кэширования ответов API.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # Формируем ключ кэша
            cache_parts = [key_prefix]
            
            if user_based and request.user.is_authenticated:
                cache_parts.append(str(request.user.id))
            
            # Добавляем хеш тела запроса
            body_hash = hashlib.md5(request.body).hexdigest()
            cache_parts.append(body_hash)
            
            cache_key = "_".join(cache_parts)
            
            # Проверяем кэш
            cached_response = cache.get(cache_key)
            if cached_response:
                return Response({
                    **cached_response,
                    'from_cache': True,
                    'cached_at': cached_response.get('cached_at', time.time())
                })
            
            # Выполняем view
            response = view_func(self, request, *args, **kwargs)
            
            # Сохраняем в кэш, если успешный ответ
            if hasattr(response, 'data') and response.status_code == 200:
                cache_data = {**response.data}
                cache_data.pop('from_cache', None)
                cache_data.pop('cached_at', None)
                cache.set(cache_key, cache_data, timeout)
            
            return response
        return wrapper
    return decorator


def validate_request(serializer_class):
    """
    Декоратор для валидации входящих данных через сериализатор.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            serializer = serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Добавляем валидированные данные в request
            request.validated_data = serializer.validated_data
            
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator
