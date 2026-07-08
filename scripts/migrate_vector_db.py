"""
Миграция базы данных для добавления векторной колонки
"""
import os
import sys
import django
import sqlite3
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings


def migrate_database():
    """Обновление структуры базы данных"""
    
    db_path = Path(settings.BASE_DIR) / 'vector_db.sqlite3'
    
    print(f" База данных: {db_path}")
    
    if not db_path.exists():
        print(" База данных не существует. Создаем новую...")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Проверяем структуру таблицы
    cursor.execute("PRAGMA table_info(documents)")
    columns = [col[1] for col in cursor.fetchall()]
    
    print(f" Текущие колонки: {columns}")
    
    # Добавляем колонку vector если её нет
    if 'vector' not in columns:
        print(" Добавляем колонку vector...")
        
        # Создаем временную таблицу с новой структурой
        cursor.execute("""
            CREATE TABLE documents_new (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                category TEXT,
                tags TEXT,
                vector TEXT
            )
        """)
        
        # Копируем данные
        cursor.execute("""
            INSERT INTO documents_new (id, title, content, category, tags)
            SELECT id, title, content, category, tags FROM documents
        """)
        
        # Удаляем старую таблицу
        cursor.execute("DROP TABLE documents")
        
        # Переименовываем новую
        cursor.execute("ALTER TABLE documents_new RENAME TO documents")
        
        # Создаем индекс
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_category ON documents (category)")
        
        print(" Колонка vector добавлена!")
    else:
        print(" Колонка vector уже существует")
    
    # Проверяем количество записей
    cursor.execute("SELECT COUNT(*) FROM documents")
    count = cursor.fetchone()[0]
    print(f" Всего документов: {count}")
    
    conn.commit()
    conn.close()
    
    print(" Миграция завершена!")


if __name__ == "__main__":
    migrate_database()
