from django.contrib import admin
from .models import NewsArticle

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'category', 'published_at')
    list_filter = ('source', 'category', 'published_at')
    search_fields = ('title', 'summary')
    readonly_fields = ('created_at',)
