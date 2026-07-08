from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'doc_type', 'created_at')
    list_filter = ('doc_type', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at',)
