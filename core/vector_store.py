"""
Векторное хранилище на основе SQLite (без расширений)
"""
import json
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
import math

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Документ с вектором"""
    id: int
    title: str
    content: str
    category: str
    tags: str
    vector: Optional[List[float]] = None
    distance: Optional[float] = None


class VectorStore:
    """
    Векторное хранилище на основе SQLite.
    Векторы хранятся как JSON, поиск выполняется в Python.
    """
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path(settings.BASE_DIR) / 'vector_db.sqlite3'
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Создание таблиц"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Основная таблица с документами и векторами
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    category TEXT,
                    tags TEXT,
                    vector TEXT  -- JSON строка с вектором
                )
            """)
            
            # Создаем индекс для ускорения поиска
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_category 
                ON documents (category)
            """)
            
            conn.commit()
    
    def add_document(self, title: str, content: str, category: str, tags: str, vector: List[float]) -> int:
        """
        Добавление документа с вектором.
        """
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            vector_json = json.dumps(vector)
            cursor.execute("""
                INSERT INTO documents (title, content, category, tags, vector)
                VALUES (?, ?, ?, ?, ?)
            """, (title, content, category, tags, vector_json))
            
            conn.commit()
            return cursor.lastrowid
    
    def search(self, query_vector: List[float], top_k: int = 5) -> List[VectorDocument]:
        """
        Поиск похожих документов по вектору.
        Вычисляет косинусное расстояние в Python.
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Получаем все документы с векторами
                cursor.execute("""
                    SELECT id, title, content, category, tags, vector
                    FROM documents
                    WHERE vector IS NOT NULL
                """)
                
                results = cursor.fetchall()
                
                if not results:
                    return []
                
                # Вычисляем расстояние для каждого документа
                scored_results = []
                query_np = np.array(query_vector)
                
                for row in results:
                    doc_vector = json.loads(row[5])
                    doc_np = np.array(doc_vector)
                    
                    # Косинусное расстояние
                    distance = self._cosine_distance(query_np, doc_np)
                    
                    scored_results.append({
                        'id': row[0],
                        'title': row[1],
                        'content': row[2],
                        'category': row[3],
                        'tags': row[4],
                        'distance': distance
                    })
                
                # Сортируем по расстоянию (чем меньше, тем ближе)
                scored_results.sort(key=lambda x: x['distance'])
                
                # Возвращаем top_k результатов
                return [
                    VectorDocument(
                        id=r['id'],
                        title=r['title'],
                        content=r['content'],
                        category=r['category'],
                        tags=r['tags'],
                        distance=r['distance']
                    )
                    for r in scored_results[:top_k]
                ]
                
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    def search_by_keywords(self, query: str, top_k: int = 5) -> List[VectorDocument]:
        """
        Полнотекстовый поиск по ключевым словам (fallback).
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                words = query.lower().split()
                conditions = []
                params = []
                
                for word in words:
                    if len(word) > 2:
                        conditions.append("title LIKE ? OR content LIKE ? OR tags LIKE ?")
                        params.extend([f"%{word}%", f"%{word}%", f"%{word}%"])
                
                if conditions:
                    sql = f"""
                        SELECT id, title, content, category, tags
                        FROM documents
                        WHERE {' OR '.join(conditions)}
                        LIMIT ?
                    """
                    params.append(top_k)
                    cursor.execute(sql, params)
                else:
                    cursor.execute("""
                        SELECT id, title, content, category, tags
                        FROM documents
                        LIMIT ?
                    """, [top_k])
                
                results = cursor.fetchall()
                
                return [
                    VectorDocument(
                        id=row[0],
                        title=row[1],
                        content=row[2],
                        category=row[3],
                        tags=row[4]
                    )
                    for row in results
                ]
                
        except Exception as e:
            logger.error(f"Keyword search error: {e}")
            return []
    
    @staticmethod
    def _cosine_distance(v1: np.ndarray, v2: np.ndarray) -> float:
        """
        Вычисляет косинусное расстояние между двумя векторами.
        """
        # Нормализация
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 1.0
        
        # Косинусное расстояние = 1 - косинусное сходство
        cosine_similarity = np.dot(v1, v2) / (norm1 * norm2)
        return 1 - cosine_similarity
    
    def get_all_documents(self) -> List[VectorDocument]:
        """Получение всех документов"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, content, category, tags
                FROM documents
            """)
            results = cursor.fetchall()
            
            return [
                VectorDocument(
                    id=row[0],
                    title=row[1],
                    content=row[2],
                    category=row[3],
                    tags=row[4]
                )
                for row in results
            ]
    
    def clear(self):
        """Очистка всех данных"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents")
            conn.commit()
    
    def count(self) -> int:
        """Количество документов"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            return cursor.fetchone()[0]
