import os
import sys
import django
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from taxes.models import TaxCalculation
from chat.models import ChatHistory

User = get_user_model()

def create_dashboard_data():
    """Создание тестовых данных для дашборда"""
    
    # Получаем или создаем пользователя
    user, created = User.objects.get_or_create(
        username='driver_demo',
        defaults={
            'email': 'driver@demo.com',
            'password': 'demo123',
            'role': 'driver',
            'status': 'self_employed',
            'region': 'Москва',
            'total_income': 150000,
            'documents_verified': True
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        print(f"Создан пользователь: {user.username}")
    else:
        print(f"Пользователь уже существует: {user.username}")
    
    # Создаем налоговые расчеты за последние 7 дней
    questions = [
        "Как получить разрешение на такси?",
        "Сколько налогов платит самозанятый?",
        "Как открыть ИП для такси?",
        "Какие выплаты у водителей?",
        "Как зарегистрироваться в Яндекс Про?",
        "Что делать при превышении лимита?",
        "Как получить карту Яндекс Про?",
        "Какие документы нужны для такси?",
        "Как платить налоги?",
        "Что такое парковая самозанятость?"
    ]
    
    intents = ['documents', 'taxes', 'payments', 'general']
    
    # Создаем записи за последние 7 дней
    for day in range(7):
        date = datetime.now().date() - timedelta(days=day)
        
        # Налоговый расчет
        income = random.randint(5000, 30000)
        TaxCalculation.objects.create(
            user=user,
            income=income,
            tax_amount=income * 0.04,
            tax_rate=4.0,
            status='self_employed',
            region='Москва',
            created_at=datetime.combine(date, datetime.now().time())
        )
        
        # 2-5 вопросов в день
        for _ in range(random.randint(2, 5)):
            question = random.choice(questions)
            intent = random.choice(intents)
            ChatHistory.objects.create(
                user=user,
                question=question,
                answer=f"Ответ на вопрос: {question}",
                intent=intent,
                confidence=random.uniform(0.3, 0.9),
                tokens_used=random.randint(50, 200),
                response_time=random.uniform(1.0, 5.0),
                context={'status': 'self_employed', 'region': 'Москва'},
                created_at=datetime.combine(date, datetime.now().time())
            )
    
    print("Тестовые данные для дашборда созданы!")
    print(f"Пользователей: {User.objects.count()}")
    print(f"Налоговых расчетов: {TaxCalculation.objects.count()}")
    print(f"Истории чатов: {ChatHistory.objects.count()}")

if __name__ == "__main__":
    create_dashboard_data()
