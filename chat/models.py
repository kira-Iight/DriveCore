# chat/models.py
from django.db import models
from django.conf import settings

class ChatHistory(models.Model):
    """История чатов с ИИ"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chats'
    )
    question = models.TextField('Вопрос')
    answer = models.TextField('Ответ')
    intent = models.CharField('Интент', max_length=50, blank=True)
    confidence = models.FloatField('Уверенность', default=0)
    tokens_used = models.IntegerField('Токенов использовано', default=0)
    response_time = models.FloatField('Время ответа (сек)', default=0)
    is_helpful = models.BooleanField('Помогло?', null=True, blank=True)
    
    context = models.JSONField('Контекст', default=dict)
    meta = models.JSONField('Метаданные', default=dict)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        verbose_name = 'История чата'
        verbose_name_plural = 'Истории чатов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.question[:50]}..."

class IntentLog(models.Model):
    """Лог классификации интентов"""
    
    INTENT_CHOICES = [
        ('tax', 'Налоги'),
        ('documents', 'Документы'),
        ('payments', 'Выплаты'),
        ('support', 'Поддержка'),
        ('general', 'Общий'),
        ('unknown', 'Неизвестный'),
    ]
    
    text = models.TextField('Текст')
    predicted_intent = models.CharField('Предсказанный интент', max_length=20, choices=INTENT_CHOICES)
    confidence = models.FloatField('Уверенность')
    is_correct = models.BooleanField('Верный', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лог интента'
        verbose_name_plural = 'Логи интентов'