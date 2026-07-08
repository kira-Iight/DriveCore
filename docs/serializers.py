from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    """Сериализатор для документов"""
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'doc_type', 'content', 'file_path', 'created_at']
        read_only_fields = ['id', 'created_at']
