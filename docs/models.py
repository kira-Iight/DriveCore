from django.db import models
from django.conf import settings

class Document(models.Model):
    """Документ"""
    
    DOC_TYPES = [
        ('report', 'Отчет'),
        ('certificate', 'Справка'),
        ('contract', 'Договор'),
        ('invoice', 'Счет'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField('Название', max_length=200)
    doc_type = models.CharField('Тип', max_length=20, choices=DOC_TYPES)
    content = models.JSONField('Содержание', default=dict)
    file_path = models.CharField('Путь к файлу', max_length=500, blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
