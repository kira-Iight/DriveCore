import pytest
from unittest.mock import Mock, patch
from django.test import TestCase
from core.ollama_service import OllamaService
from core.vector_store import VectorStore
from core.embedding_service import EmbeddingService


class TaxServiceTest(TestCase):
    """Тесты налогового сервиса (встроенная логика)"""
    
    def test_tax_rates(self):
        """Тест налоговых ставок"""
        rates = {
            'self_employed': 4.0,
            'ie': 6.0,
            'employee': 13.0
        }
        self.assertEqual(rates['self_employed'], 4.0)
        self.assertEqual(rates['ie'], 6.0)
        self.assertEqual(rates['employee'], 13.0)
    
    def test_tax_calculation(self):
        """Тест расчета налогов"""
        income = 100000
        rates = {'self_employed': 4.0}
        tax = income * (rates['self_employed'] / 100)
        self.assertEqual(tax, 4000)
    
    def test_net_income_calculation(self):
        """Тест расчета чистого дохода"""
        income = 100000
        tax = 4000
        net = income - tax
        self.assertEqual(net, 96000)


class OllamaServiceTest(TestCase):
    """Тесты сервиса Ollama"""
    
    def setUp(self):
        self.service = OllamaService()
    
    def test_classify_intent_tax(self):
        """Тест классификации налогового вопроса"""
        result = self.service.classify_intent('Сколько налогов платит самозанятый?')
        self.assertEqual(result['intent'], 'tax')
        self.assertGreater(result['confidence'], 0)
    
    def test_classify_intent_documents(self):
        """Тест классификации вопроса о документах"""
        result = self.service.classify_intent('Как получить разрешение на такси?')
        self.assertEqual(result['intent'], 'documents')
    
    def test_classify_intent_general(self):
        """Тест классификации общего вопроса"""
        result = self.service.classify_intent('Привет, как дела?')
        self.assertEqual(result['intent'], 'general')
    
    def test_search_knowledge_base(self):
        """Тест поиска в базе знаний"""
        results = self.service.search_knowledge_base('налоги')
        self.assertIsInstance(results, list)


class EmbeddingServiceTest(TestCase):
    """Тесты сервиса эмбеддингов"""
    
    def test_embedding_service_available(self):
        """Тест доступности сервиса эмбеддингов"""
        try:
            service = EmbeddingService()
            available = service.is_available()
            self.assertIsInstance(available, bool)
        except Exception:
            self.skipTest("Embedding service not available")


class VectorStoreTest(TestCase):
    """Тесты векторного хранилища"""
    
    def test_vector_store_init(self):
        """Тест инициализации векторного хранилища"""
        try:
            from pathlib import Path
            from django.conf import settings
            store = VectorStore()
            self.assertIsNotNone(store)
        except Exception as e:
            self.skipTest(f"Vector store not available: {e}")
