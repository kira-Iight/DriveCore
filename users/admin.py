from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админка для пользователей"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'status', 'region')
    list_filter = ('role', 'status', 'region', 'documents_verified')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'role', 'status', 'region', 'phone', 'telegram_id',
                'total_income', 'tax_paid', 'tax_rate',
                'documents_verified', 'has_patent', 'patent_region'
            )
        }),
    )
