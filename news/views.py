from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import NewsArticle
from .serializers import NewsArticleSerializer

class NewsViewSet(viewsets.ModelViewSet):
    """API для новостей"""
    
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.order_by('-published_at')
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Получение последних новостей"""
        limit = request.query_params.get('limit', 10)
        news = self.queryset.order_by('-published_at')[:int(limit)]
        serializer = self.get_serializer(news, many=True)
        return Response(serializer.data)
