from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """Кастомная модель пользователя"""
    
    ROLE_CHOICES = [
        ('driver', 'Водитель'),
        ('team', 'Команда'),
        ('gov', 'Госорганы'),
    ]
    
    STATUS_CHOICES = [
        ('self_employed', 'Самозанятый'),
        ('ie', 'ИП'),
        ('employee', 'Наёмный работник'),
    ]
    
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='driver')
    status = models.CharField('Статус', max_length=30, choices=STATUS_CHOICES, default='self_employed')
    region = models.CharField('Регион', max_length=100, default='Москва')
    telegram_id = models.CharField('Telegram ID', max_length=50, blank=True, null=True, unique=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    
    # Финансовые данные
    total_income = models.DecimalField('Общий доход', max_digits=12, decimal_places=2, default=0)
    tax_paid = models.DecimalField('Уплачено налогов', max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField('Налоговая ставка', max_digits=5, decimal_places=2, default=4)
    
    # Документы
    documents_verified = models.BooleanField('Документы проверены', default=False)
    has_patent = models.BooleanField('Есть патент', default=False)
    patent_region = models.CharField('Регион патента', max_length=100, blank=True)
    
    # Метаданные
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    last_active = models.DateTimeField('Последняя активность', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def remaining_limit(self):
        """Остаток лимита для самозанятых (2.4 млн)"""
        if self.status == 'self_employed':
            return 2400000 - float(self.total_income)
        return None
    
    def is_driver(self):
        return self.role == 'driver'
    
    def is_team(self):
        return self.role == 'team'
    
    def is_gov(self):
        return self.role == 'gov'
