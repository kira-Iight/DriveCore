from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db.models import Sum, Count, Avg
from django.contrib.auth import get_user_model
from django.utils import timezone
import time  # <--- ДОБАВИТЬ ЭТУ СТРОКУ

from chat.models import ChatHistory
from taxes.models import TaxCalculation

User = get_user_model()


class AnalyticsViewSet(viewsets.ViewSet):
    """API для аналитики"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Получение статистики с кэшированием"""
        user_id = request.user.id
        
        # Ключ для кэша
        cache_key = f"analytics_stats_{user_id}"
        
        # Проверяем кэш
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return Response({
                **cached_stats,
                'from_cache': True
            })
        
        # Собираем статистику
        total_users = User.objects.count()
        drivers_count = User.objects.filter(role='driver').count()
        team_count = User.objects.filter(role='team').count()
        gov_count = User.objects.filter(role='gov').count()
        
        # Доходы
        total_income = TaxCalculation.objects.aggregate(
            total=Sum('income')
        )['total'] or 0
        
        # Чаты
        total_chats = ChatHistory.objects.count()
        
        # Активность сегодня
        today = timezone.now().date()
        active_today = ChatHistory.objects.filter(
            created_at__date=today
        ).count()
        
        # Последние вопросы
        recent_questions = ChatHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5].values('question', 'created_at')
        
        stats = {
            'users': {
                'total': total_users,
                'drivers': drivers_count,
                'team': team_count,
                'gov': gov_count
            },
            'finances': {
                'total_income': float(total_income),
                'avg_income': float(total_income / drivers_count) if drivers_count > 0 else 0
            },
            'activity': {
                'total_chats': total_chats,
                'active_today': active_today
            },
            'recent_questions': list(recent_questions),
            'cached_at': time.time()
        }
        
        # Кэшируем на 5 минут
        cache.set(cache_key, stats, timeout=300)
        
        return Response({
            **stats,
            'from_cache': False
        })
    
    @action(detail=False, methods=['get'])
    def detailed(self, request):
        """Детальная статистика (администраторы)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Только для администраторов'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        cache_key = 'analytics_detailed'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response({
                **cached_data,
                'from_cache': True
            })
        
        data = {
            'users_by_role': {
                'driver': User.objects.filter(role='driver').count(),
                'team': User.objects.filter(role='team').count(),
                'gov': User.objects.filter(role='gov').count()
            },
            'users_by_status': {
                'self_employed': User.objects.filter(status='self_employed').count(),
                'ie': User.objects.filter(status='ie').count(),
                'employee': User.objects.filter(status='employee').count()
            },
            'chats_by_intent': {
                'tax': ChatHistory.objects.filter(intent='tax').count(),
                'documents': ChatHistory.objects.filter(intent='documents').count(),
                'payments': ChatHistory.objects.filter(intent='payments').count(),
                'support': ChatHistory.objects.filter(intent='support').count()
            },
            'total_tax_collected': TaxCalculation.objects.aggregate(
                total=Sum('tax_amount')
            )['total'] or 0
        }
        
        cache.set(cache_key, data, timeout=3600)
        
        return Response({
            **data,
            'from_cache': False
        })
    
    @action(detail=False, methods=['get'])
    def problems(self, request):
        """Получение данных о проблемах (мониторинг жалоб)"""
        alerts = cache.get('complaints_alerts')
        
        if not alerts:
            return Response({
                'message': 'Нет данных о проблемах',
                'alerts': [],
                'total': 0,
                'by_city': {},
                'recent': []
            })
        
        return Response({
            'timestamp': alerts.get('timestamp'),
            'total': alerts.get('total', 0),
            'by_city': alerts.get('by_city', {}),
            'alerts': alerts.get('alerts', []),
            'recent': alerts.get('recent', [])
        })
