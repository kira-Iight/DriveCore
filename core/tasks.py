import logging
import feedparser
import requests
from datetime import datetime, timedelta
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from chat.models import ChatHistory
from news.models import NewsArticle
from taxes.models import TaxCalculation
import os

logger = logging.getLogger(__name__)
User = get_user_model()

# Ключевые слова для фильтрации новостей по ПЗ
PLATFORM_KEYWORDS = [
    'такси', 'самозанят', 'ИП', 'платформенн', 'занятость',
    'гиг-экономик', 'водител', 'курьер', 'яндекс такси',
    'uber', 'bolt', 'grab', 'did', 'indrive'
]

# ТЕСТОВАЯ ЗАДАЧА
@shared_task
def debug_task():
    """Тестовая задача для проверки Celery"""
    logger.info(" Debug task executed!")
    return "Celery работает со встроенным брокером!"

# ЗАДАЧА 1: Парсинг новостей по ПЗ
@shared_task
def parse_news():
    """Парсинг новостей из RSS-лент с фильтром по платформенной занятости"""
    logger.info(" Начинаем парсинг новостей...")
    
    news_sources = [
        {'url': 'https://www.rbc.ru/rss/', 'source': 'РБК'},
        {'url': 'https://tass.ru/rss/v2.xml', 'source': 'ТАСС'},
        {'url': 'https://www.vedomosti.ru/rss', 'source': 'Ведомости'},  
       {'url': 'https://www.kommersant.ru/RSS/news.xml', 'source': 'Коммерсантъ'},   
    ]
    
    articles_added = 0
    
    for source in news_sources:
        try:
            feed = feedparser.parse(source['url'])
            
            for entry in feed.entries[:20]:
                # Проверяем, есть ли ключевые слова в заголовке или описании
                text = (entry.title + ' ' + entry.get('summary', '')).lower()
                is_platform = any(kw in text for kw in PLATFORM_KEYWORDS)
                
                if is_platform and not NewsArticle.objects.filter(url=entry.link).exists():
                    NewsArticle.objects.create(
                        title=entry.title[:500],
                        summary=entry.get('summary', '')[:500],
                        url=entry.link,
                        source=source['source'],
                        category='platform_employment',  # специальная категория
                        published_at=datetime.now()
                    )
                    articles_added += 1
            
            logger.info(f" Добавлено {articles_added} новостей из {source['source']}")
            
        except Exception as e:
            logger.error(f" Ошибка парсинга {source['source']}: {e}")
    
    cache.delete('latest_news')
    logger.info(f" Парсинг завершен! Добавлено {articles_added} новостей по теме ПЗ")
    return f"Добавлено {articles_added} новостей по теме платформенной занятости"

# ЗАДАЧА 2: Мониторинг проблем
@shared_task
def monitor_problems():
    """Мониторинг жалоб с оповещением о всплесках"""
    logger.info(" Начинаем мониторинг проблем...")
    
    # Анализируем последние 2 часа
    two_hours_ago = timezone.now() - timedelta(hours=2)
    recent_chats = ChatHistory.objects.filter(
        created_at__gte=two_hours_ago
    )
    
    # Ключевые слова для жалоб
    complaint_keywords = [
        'проблем', 'ошибк', 'не работа', 'сбой', 'баг',
        'жалоб', 'недовол', 'плох', 'ужасн',
        'деньг', 'выплат', 'не получ', 'задержк'
    ]
    
    # Группируем по городу
    problems_by_city = {}
    complaints = []
    
    for chat in recent_chats:
        question_lower = chat.question.lower()
        
        # Проверяем наличие жалоб
        for keyword in complaint_keywords:
            if keyword in question_lower:
                city = chat.context.get('region', 'неизвестный город')
                if city not in problems_by_city:
                    problems_by_city[city] = []
                problems_by_city[city].append({
                    'user_id': chat.user_id,
                    'question': chat.question[:100],
                    'keyword': keyword,
                    'created_at': chat.created_at
                })
                complaints.append({
                    'city': city,
                    'question': chat.question[:100],
                    'keyword': keyword
                })
                break
    
    # Проверяем всплески жалоб
    alerts = []
    for city, city_complaints in problems_by_city.items():
        count = len(city_complaints)
        if count >= 3:  # порог для оповещения
            alert = f" За последние 2 часа зафиксировано {count} жалоб в городе {city}"
            alerts.append(alert)
            logger.warning(alert)
    
    # Сохраняем в кэш для API
    cache.set('complaints_alerts', {
        'timestamp': timezone.now().isoformat(),
        'total': len(complaints),
        'by_city': {city: len(c) for city, c in problems_by_city.items()},
        'alerts': alerts,
        'recent': complaints[:10]
    }, timeout=7200)
    
    logger.info(f" Мониторинг завершен: {len(complaints)} жалоб, {len(alerts)} оповещений")
    return {
        'total_complaints': len(complaints),
        'alerts': alerts,
        'by_city': {city: len(c) for city, c in problems_by_city.items()}
    }

# ЗАДАЧА 3: Ежедневный дайджест новостей

@shared_task
def send_daily_digest():
    """Ежедневный дайджест с отправкой в Telegram"""
    today = timezone.now().date()
    
    # Новости за сегодня
    today_news = NewsArticle.objects.filter(
        created_at__date=today,
        category='platform_employment'
    ).order_by('-created_at')[:10]
    
    # Формируем дайджест
    digest = f" Ежедневный дайджест {today.strftime('%d.%m.%Y')}\n\n"
    digest += f" Новости ({today_news.count()}):\n"
    for news in today_news:
        digest += f"• {news.title}\n{news.url}\n"
    
    # Отправка в Telegram
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '1126146152')  # ID канала
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={'chat_id': chat_id, 'text': digest})
        logger.info(f" Дайджест отправлен в Telegram")
    except Exception as e:
        logger.error(f" Ошибка отправки в Telegram: {e}")
    
    return digest

# ЗАДАЧА 4: Очистка старых данных
@shared_task
def cleanup_old_data():
    """Очистка старых данных (раз в неделю)"""
    logger.info(" Начинаем очистку старых данных...")
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    old_chats = ChatHistory.objects.filter(created_at__lt=thirty_days_ago)
    chats_deleted = old_chats.count()
    old_chats.delete()
    
    logger.info(f" Очищено: {chats_deleted} чатов")
    return f"Удалено {chats_deleted} чатов"


@shared_task
def send_telegram_message(message):
    import requests
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={'chat_id': chat_id, 'text': message})