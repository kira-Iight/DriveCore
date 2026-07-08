from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import TaxCalculation
from .serializers import TaxCalculationSerializer
import hashlib
import time


class TaxViewSet(viewsets.ModelViewSet):
    """API для налоговых расчетов"""
    
    queryset = TaxCalculation.objects.all()
    serializer_class = TaxCalculationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Расчет налогов"""
        income = request.data.get('income', 0)
        status = request.data.get('status', 'self_employed')
        region = request.data.get('region', 'Москва')
        user = request.user
        
        tax_rates = {
            'self_employed': 4.0,
            'ie': 6.0,
            'employee': 13.0
        }
        
        rate = tax_rates.get(status, 4.0)
        tax_amount = float(income) * (rate / 100)
        
        calculation = TaxCalculation.objects.create(
            user=user,
            income=income,
            tax_amount=tax_amount,
            tax_rate=rate,
            status=status,
            region=region
        )
        
        return Response({
            'id': calculation.id,
            'income': income,
            'tax_rate': rate,
            'tax_amount': tax_amount,
            'status': status,
            'region': region
        })
    
    @action(detail=False, methods=['get'])
    def rates(self, request):
        """Получение всех налоговых ставок"""
        rates = {
            'self_employed': {
                'rate': 4.0,
                'description': 'Самозанятый (4% с физлиц, 6% с юрлиц)',
                'limit': 2400000
            },
            'ie': {
                'rate': 6.0,
                'description': 'Индивидуальный предприниматель (УСН 6%)',
                'limit': None
            },
            'employee': {
                'rate': 13.0,
                'description': 'Наёмный работник (НДФЛ 13%)',
                'limit': None
            }
        }
        
        return Response({'rates': rates})
