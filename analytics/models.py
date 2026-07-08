from django.db import models

class Dashboard(models.Model):
    """Дашборд аналитики"""
    
    name = models.CharField('Название', max_length=100)
    data = models.JSONField('Данные', default=dict)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Дашборд'
        verbose_name_plural = 'Дашборды'
    
    def __str__(self):
        return self.name
