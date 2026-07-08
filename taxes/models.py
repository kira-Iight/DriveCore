from django.db import models
from django.conf import settings

class TaxCalculation(models.Model):
    """Расчет налогов"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tax_calculations'
    )
    income = models.DecimalField('Доход', max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField('Сумма налога', max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField('Ставка налога', max_digits=5, decimal_places=2)
    status = models.CharField('Статус', max_length=30)
    region = models.CharField('Регион', max_length=100)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Расчет налога'
        verbose_name_plural = 'Расчеты налогов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.income} - {self.tax_amount}"
