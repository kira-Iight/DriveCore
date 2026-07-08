from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """API для управления пользователями"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Ограничение доступа к данным"""
        user = self.request.user
        
        # Команда и госорганы видят всех
        if user.role in ['team', 'gov']:
            return User.objects.all()
        
        # Водители видят только себя
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'], url_path='me')
    def get_me(self, request):
        """Получение данных текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'], url_path='me')
    def update_me(self, request):
        """Обновление данных текущего пользователя"""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
