from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Document
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ModelViewSet):
    """API для документов"""
    
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Генерация документа"""
        doc_type = request.data.get('type', 'report')
        data = request.data.get('data', {})
        
        # Простая генерация
        document = Document.objects.create(
            user=request.user,
            title=f"Документ {doc_type}",
            doc_type=doc_type,
            content=data,
            file_path=f"documents/{request.user.id}_{doc_type}.pdf"
        )
        
        return Response({
            'id': document.id,
            'title': document.title,
            'doc_type': document.doc_type,
            'created_at': document.created_at
        })
