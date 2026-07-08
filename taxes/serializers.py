from rest_framework import serializers
from .models import TaxCalculation


class TaxCalculationRequestSerializer(serializers.Serializer):
    """Сериализатор для валидации запроса на расчет налогов"""
    
    income = serializers.FloatField(
        min_value=0,
        required=True,
        error_messages={
            'min_value': 'Доход не может быть отрицательным',
            'required': 'Доход обязателен'
        }
    )
    
    status = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Статус обязателен'
        }
    )
    
    region = serializers.CharField(
        required=False,
        default='Москва'
    )
    
    def validate_status(self, value):
        """Валидация статуса"""
        valid_statuses = ['self_employed', 'ie', 'employee']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Неизвестный статус: {value}. Доступные: {valid_statuses}"
            )
        return value


class TaxCalculationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели TaxCalculation"""
    
    class Meta:
        model = TaxCalculation
        fields = [
            'id', 'income', 'tax_amount', 'tax_rate',
            'status', 'region', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
