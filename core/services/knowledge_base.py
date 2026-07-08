"""
База знаний с поддержкой векторного поиска
"""
import logging
from typing import List, Dict, Any
from pathlib import Path
from django.conf import settings

from core.vector_store import VectorStore
from core.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    База знаний с гибридным поиском:
    1. Векторный поиск (по смыслу)
    2. Полнотекстовый поиск (по словам)
    """
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedding_service = EmbeddingService()
        self._ensure_initialized()
    
    def _ensure_initialized(self):
        """Инициализация БЗ тестовыми данными если пуста"""
        if self.vector_store.count() == 0:
            self.init_test_data()
            logger.info(" База знаний инициализирована тестовыми данными")
    
    def search(self, query: str, top_k: int = 5, use_vectors: bool = True) -> List[Dict[str, Any]]:
        """Поиск в базе знаний"""
        # Сначала пробуем векторный поиск
        if use_vectors and self.embedding_service.is_available():
            query_vector = self.embedding_service.get_embedding(query)
            if query_vector:
                results = self.vector_store.search(query_vector, top_k)
                if results:
                    return [
                        {
                            'title': doc.title,
                            'content': doc.content,
                            'category': doc.category,
                            'tags': doc.tags,
                            'score': 1 - (doc.distance or 0.5),
                            'search_type': 'vector'
                        }
                        for doc in results
                    ]
        
        # Fallback: полнотекстовый поиск
        logger.info("Using fallback: full-text search")
        return self.full_text_search(query, top_k)
    
    def full_text_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Полнотекстовый поиск по ключевым словам"""
        results = self.vector_store.search_by_keywords(query, top_k)
        return [
            {
                'title': doc.title,
                'content': doc.content,
                'category': doc.category,
                'tags': doc.tags,
                'search_type': 'full_text'
            }
            for doc in results
        ]
    
    def add_document(self, title: str, content: str, category: str, tags: str):
        """Добавление документа с генерацией вектора"""
        text_for_embedding = f"{title} {content}"
        vector = self.embedding_service.get_embedding(text_for_embedding)
        
        if vector:
            self.vector_store.add_document(title, content, category, tags, vector)
            logger.info(f" Добавлен документ с вектором: {title}")
        else:
            self.vector_store.add_document(title, content, category, tags, [0.0] * 384)
            logger.warning(f" Добавлен документ без вектора: {title}")
    
    def init_test_data(self):
        """Инициализация тестовыми данными"""
        test_data = [
            (
                "Налоги для самозанятых водителей",
                "Самозанятые платят 4% с физлиц и 6% с юрлиц. Лимит 2.4 млн ₽ в год.",
                "taxes",
                "налог,самозанятый,4%,6%"
            ),
            (
                "Разница между самозанятым и ИП",
                "Самозанятый: 4-6%, лимит 2.4 млн, без взносов. ИП: 6% или патент, без лимита, с взносами.",
                "taxes",
                "самозанятый,ИП,разница"
            ),
            (
                "Как получить разрешение на такси в Москве",
                "Подайте заявление через Госуслуги или МФЦ. Срок 6 рабочих дней. Нужны: СТС, паспорт, договор с Яндекс Про.",
                "documents",
                "разрешение,такси,Москва"
            ),
            (
                "Как открыть ИП для такси",
                "1. Выберите УСН 6% или патент. 2. Укажите ОКВЭД 49.32. 3. Подайте заявление в ФНС. 4. Откройте расчетный счет.",
                "documents",
                "ИП,регистрация,ОКВЭД"
            ),
            (
                "Выплаты на карту Яндекс Про",
                "Моментальные выплаты, без комиссии. Кешбэк до 10%. Минимальная сумма: 100 ₽.",
                "payments",
                "выплаты,карта,Яндекс Про"
            ),
        ]
        
        for title, content, category, tags in test_data:
            self.add_document(title, content, category, tags)
        
        logger.info(f" Добавлено {len(test_data)} документов в БЗ")
    
    def get_stats(self) -> Dict[str, Any]:
        """Статистика базы знаний"""
        return {
            'total_documents': self.vector_store.count(),
            'embedding_available': self.embedding_service.is_available(),
        }
