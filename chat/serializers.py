from rest_framework import serializers
from .models import ChatHistory


class ChatHistorySerializer(serializers.ModelSerializer):
    """Сериализатор для истории чата"""
    
    class Meta:
        model = ChatHistory
        fields = [
            'id', 'question', 'answer', 'intent',
            'confidence', 'response_time', 'is_helpful',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class QuestionSerializer(serializers.Serializer):
    """Сериализатор для валидации вопроса"""
    
    question = serializers.CharField(
        max_length=1000,
        min_length=3,
        required=True,
        error_messages={
            'min_length': 'Вопрос должен содержать минимум 3 символа',
            'max_length': 'Вопрос не может превышать 1000 символов',
            'required': 'Вопрос обязателен'
        }
    )
    
    def validate_question(self, value):
        """Валидация вопроса"""
        # Удаляем лишние пробелы
        value = ' '.join(value.split())
        
        if len(value) < 3:
            raise serializers.ValidationError("Вопрос слишком короткий")
        
        return value
