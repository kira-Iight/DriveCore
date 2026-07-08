from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import ChatHistory
from .serializers import ChatHistorySerializer, QuestionSerializer
from core.ollama_service import OllamaService
from core.decorators import validate_request
import time
import hashlib


class ChatViewSet(viewsets.ModelViewSet):
    """
    API для чат-бота с кэшированием.
    Использует OllamaService для генерации ответов.
    """
    
    queryset = ChatHistory.objects.all()
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def _get_cache_key(self, user_id: int, question: str) -> str:
        """Генерирует ключ для кэша"""
        question_hash = hashlib.md5(question.encode()).hexdigest()
        return f"chat_{user_id}_{question_hash}"
    
    @action(detail=False, methods=['post'])
    @validate_request(QuestionSerializer)
    def ask(self, request):
        """
        Задать вопрос ИИ с кэшированием.
        """
        question = request.validated_data['question']
        user = request.user
        
        # Проверяем кэш
        cache_key = self._get_cache_key(user.id, question)
        cached_response = cache.get(cache_key)
        
        if cached_response:
            return Response({
                'answer': cached_response['answer'],
                'intent': cached_response['intent'],
                'confidence': cached_response['confidence'],
                'from_cache': True,
                'cached_at': cached_response.get('cached_at')
            })
        
        # Контекст пользователя
        user_context = {
            'full_name': user.get_full_name() or user.username,
            'status': user.status,
            'region': user.region,
            'income': float(user.total_income) if user.total_income else 0,
        }
        
        # Инициализация AI
        ai_service = OllamaService()
        
        # Классификация
        intent_result = ai_service.classify_intent(question)
        
        # Поиск в БЗ (с векторами)
        context_docs = ai_service.search_knowledge_base(question)
        
        # Генерация ответа
        start_time = time.time()
        response = ai_service.generate_response(question, user_context, context_docs)
        response_time = time.time() - start_time
        
        #  Сохраняем в кэш на 1 час
        cache_data = {
            'answer': response['answer'],
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'cached_at': time.time()
        }
        cache.set(cache_key, cache_data, timeout=3600)
        
        # Сохранение в БД
        chat = ChatHistory.objects.create(
            user=user,
            question=question,
            answer=response['answer'],
            intent=intent_result['intent'],
            confidence=intent_result['confidence'],
            tokens_used=response.get('tokens', 0),
            response_time=response_time,
            context=user_context
        )
        
        return Response({
            'id': chat.id,
            'answer': response['answer'],
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'response_time': response_time,
            'from_cache': False,
            'vector_search_used': bool(context_docs)
        })
    
    @action(detail=False, methods=['post'])
    def clear_cache(self, request):
        """Очистка кэша (только для администраторов)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Только для администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        cache.clear()
        return Response({
            'message': ' Кэш успешно очищен',
            'timestamp': time.time()
        })
    
    @action(detail=False, methods=['get'])
    def cache_stats(self, request):
        """Статистика кэша (только для администраторов)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Только для администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM cache_table")
            count = cursor.fetchone()[0]
        
        return Response({
            'total_cached_items': count,
            'cache_backend': 'DatabaseCache (SQLite)'
        })
