import os
import sys
import django
import sqlite3
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def clear_knowledge_base():
    """Очистка базы знаний"""
    db_path = Path(settings.BASE_DIR) / 'vector_db.sqlite3'
    
    if not db_path.exists():
        print("База данных не существует")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Очищаем таблицу документов
    cursor.execute("DELETE FROM documents")
    conn.commit()
    
    # Проверяем количество записей
    cursor.execute("SELECT COUNT(*) FROM documents")
    count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"База знаний очищена. Удалено записей: {count}")

if __name__ == "__main__":
    clear_knowledge_base()
