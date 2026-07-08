"""
Скрипт для индексации базы знаний с векторами
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.services.knowledge_base import KnowledgeBase


def index_knowledge_base():
    """Индексация базы знаний"""
    print("Начинаем индексацию базы знаний...")
    
    kb = KnowledgeBase()
    
    # Получаем статистику
    stats = kb.get_stats()
    print(f" Всего документов: {stats['total_documents']}")
    print(f" Эмбеддинги доступны: {stats['embedding_available']}")
    
    print("\n Индексация завершена!")


def add_document():
    """Добавление нового документа в БЗ"""
    print(" Добавление нового документа...")
    
    kb = KnowledgeBase()
    
    title = input("Введите заголовок: ")
    content = input("Введите содержание: ")
    category = input("Введите категорию: ")
    tags = input("Введите теги (через запятую): ")
    
    kb.add_document(title, content, category, tags)
    
    print(" Документ добавлен!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'add':
        add_document()
    else:
        index_knowledge_base()
