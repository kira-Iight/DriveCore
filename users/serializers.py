from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    
    full_name = serializers.SerializerMethodField()
    remaining_limit = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'status', 'region', 'phone',
            'telegram_id', 'total_income', 'tax_paid', 'tax_rate',
            'documents_verified', 'has_patent', 'patent_region',
            'remaining_limit', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    
    def get_remaining_limit(self, obj):
        return obj.remaining_limit

class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'status', 'region', 'phone', 'total_income',
            'documents_verified'
        ]
        read_only_fields = ['id', 'username', 'email']
