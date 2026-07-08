from rest_framework import serializers
from .models import NewsArticle

class NewsArticleSerializer(serializers.ModelSerializer):
    """Сериализатор для новостей"""
    
    class Meta:
        model = NewsArticle
        fields = [
            'id', 'title', 'summary', 'url', 'source',
            'category', 'published_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
