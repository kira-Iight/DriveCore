"""
Сервис для генерации эмбеддингов (векторов)
"""
import logging
import numpy as np
from typing import List, Optional

logger = logging.getLogger(__name__)

# Ленивая загрузка модели
_embedder = None


def get_embedder():
    """Ленивая загрузка модели эмбеддингов"""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Используем легковесную модель для русского языка
            _embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info(" Модель эмбеддингов загружена!")
        except ImportError:
            logger.warning("⚠️ Sentence-transformers не установлен")
            _embedder = None
        except Exception as e:
            logger.error(f" Ошибка загрузки модели: {e}")
            _embedder = None
    return _embedder


class EmbeddingService:
    """
    Сервис для генерации эмбеддингов текста.
    Использует sentence-transformers для создания векторных представлений.
    """
    
    @classmethod
    def get_embedding(cls, text: str) -> Optional[List[float]]:
        """
        Генерация эмбеддинга для текста.
        
        Args:
            text: Текст для векторизации
            
        Returns:
            Вектор размерности 384 или None при ошибке
        """
        embedder = get_embedder()
        if embedder is None:
            return None
        
        try:
            # Генерируем вектор
            embedding = embedder.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    @classmethod
    def get_embeddings_batch(cls, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Генерация эмбеддингов для списка текстов.
        
        Args:
            texts: Список текстов
            
        Returns:
            Список векторов
        """
        embedder = get_embedder()
        if embedder is None:
            return [None] * len(texts)
        
        try:
            embeddings = embedder.encode(texts)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [None] * len(texts)
    
    @classmethod
    def is_available(cls) -> bool:
        """Проверка доступности сервиса эмбеддингов"""
        return get_embedder() is not None
