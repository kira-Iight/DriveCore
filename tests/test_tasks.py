from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth import get_user_model
from chat.models import ChatHistory
from news.models import NewsArticle
from core.tasks import debug_task, parse_news, monitor_problems, send_daily_digest
from django.utils import timezone

User = get_user_model()


class CeleryTasksTest(TestCase):
    """Тесты Celery задач"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_debug_task(self):
        """Тест отладочной задачи"""
        result = debug_task()
        self.assertEqual(result, 'Celery работает со встроенным брокером!')
    
    def test_monitor_problems_no_complaints(self):
        """Тест мониторинга проблем без жалоб"""
        result = monitor_problems()
        self.assertEqual(result['total_complaints'], 0)
        self.assertEqual(result['alerts'], [])
    
    def test_monitor_problems_with_complaints(self):
        """Тест мониторинга проблем с жалобами"""
        # Создаем жалобы
        for i in range(4):
            ChatHistory.objects.create(
                user=self.user,
                question=f'Проблема с выплатой {i}',
                answer='Ответ',
                context={'region': 'Москва'}
            )
        
        result = monitor_problems()
        self.assertGreater(result['total_complaints'], 0)
    
    def test_send_daily_digest(self):
        """Тест отправки дайджеста"""
        # Создаем новости
        NewsArticle.objects.create(
            title='Новость 1',
            url='https://example.com/news/1',
            source='Тест',
            category='platform_employment',
            published_at=timezone.now()
        )
        NewsArticle.objects.create(
            title='Новость 2',
            url='https://example.com/news/2',
            source='Тест',
            category='platform_employment',
            published_at=timezone.now()
        )
        
        result = send_daily_digest()
        self.assertIn('Ежедневный дайджест', result)
