from django.contrib import admin
from .models import TaxCalculation

@admin.register(TaxCalculation)
class TaxCalculationAdmin(admin.ModelAdmin):
    list_display = ('user', 'income', 'tax_amount', 'tax_rate', 'status', 'created_at')
    list_filter = ('status', 'region', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
