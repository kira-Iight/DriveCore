import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from chat.models import ChatHistory
from taxes.models import TaxCalculation
from news.models import NewsArticle

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели пользователя"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            role='driver',
            status='self_employed',
            region='Москва'
        )
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'driver')
        self.assertEqual(self.user.status, 'self_employed')
    
    def test_user_str_method(self):
        """Тест строкового представления пользователя"""
        self.assertIsNotNone(str(self.user))
    
    def test_is_driver_method(self):
        """Тест метода is_driver"""
        self.assertTrue(self.user.is_driver())
        self.user.role = 'team'
        self.user.save()
        self.assertFalse(self.user.is_driver())


class ChatHistoryModelTest(TestCase):
    """Тесты модели истории чатов"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.chat = ChatHistory.objects.create(
            user=self.user,
            question='Как получить разрешение на такси?',
            answer='Ответ на вопрос',
            intent='documents',
            confidence=0.85
        )
    
    def test_chat_creation(self):
        """Тест создания записи чата"""
        self.assertEqual(self.chat.user.username, 'testuser')
        self.assertEqual(self.chat.question, 'Как получить разрешение на такси?')
        self.assertEqual(self.chat.intent, 'documents')
    
    def test_chat_str_method(self):
        """Тест строкового представления чата"""
        self.assertIsNotNone(str(self.chat))


class TaxCalculationModelTest(TestCase):
    """Тесты модели налоговых расчетов"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.tax = TaxCalculation.objects.create(
            user=self.user,
            income=100000,
            tax_amount=4000,
            tax_rate=4.0,
            status='self_employed',
            region='Москва'
        )
    
    def test_tax_creation(self):
        """Тест создания налогового расчета"""
        self.assertEqual(self.tax.income, 100000)
        self.assertEqual(self.tax.tax_amount, 4000)
        self.assertEqual(self.tax.tax_rate, 4.0)
    
    def test_tax_str_method(self):
        """Тест строкового представления налогового расчета"""
        self.assertIsNotNone(str(self.tax))


class NewsArticleModelTest(TestCase):
    """Тесты модели новостей"""
    
    def setUp(self):
        self.news = NewsArticle.objects.create(
            title='Тестовая новость',
            summary='Краткое описание',
            url='https://example.com/news/1',
            source='Тестовый источник',
            category='platform_employment',
            published_at=timezone.now()
        )
    
    def test_news_creation(self):
        """Тест создания новости"""
        self.assertEqual(self.news.title, 'Тестовая новость')
        self.assertEqual(self.news.category, 'platform_employment')
    
    def test_news_str_method(self):
        """Тест строкового представления новости"""
        self.assertEqual(str(self.news), 'Тестовая новость')
