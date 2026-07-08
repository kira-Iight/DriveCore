from django.db import models

class NewsArticle(models.Model):
    """Новостная статья"""
    
    title = models.CharField('Заголовок', max_length=500)
    summary = models.TextField('Краткое содержание', blank=True)
    full_text = models.TextField('Полный текст', blank=True)
    url = models.CharField('URL', max_length=500, unique=True)
    source = models.CharField('Источник', max_length=100)
    category = models.CharField('Категория', max_length=50, blank=True)
    published_at = models.DateTimeField('Дата публикации')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']
    
    def __str__(self):
        return self.title[:100]
