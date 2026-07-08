# chat/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from core.ollama_service import OllamaService
import time

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer для чата с ИИ"""
    
    async def connect(self):
        """Подключение клиента"""
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'chat_{self.user_id}'
        
        # Упрощенная проверка: принимаем все соединения для тестирования
        # В продакшене нужно добавить проверку токена
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Отправляем приветствие
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': 'Подключено к чату! Задайте ваш вопрос.',
            'user': {'id': self.user_id}
        }))
        
        logger.info(f"WebSocket connected: user {self.user_id}")
    
    async def disconnect(self, close_code):
        """Отключение клиента"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: user {self.user_id}, code: {close_code}")
    
    async def receive(self, text_data):
        """Получение сообщения от клиента"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'question':
                question = data.get('content', '').strip()
                if not question:
                    await self.send_error('Вопрос не может быть пустым')
                    return
                
                # Отправляем индикатор печатания
                await self.send_typing(True)
                
                # Обрабатываем вопрос
                answer = await self.process_question(question)
                
                # Отправляем ответ
                await self.send_answer(answer)
                
                # Отключаем индикатор печатания
                await self.send_typing(False)
                
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
                
            else:
                await self.send_error(f'Неизвестный тип сообщения: {message_type}')
                
        except json.JSONDecodeError:
            await self.send_error('Неверный формат сообщения')
        except Exception as e:
            logger.error(f"Error in receive: {e}")
            await self.send_error(f'Ошибка обработки: {str(e)}')
    
    async def process_question(self, question):
        """Обработка вопроса через AI сервис"""
        # Получаем пользователя
        user = await self.get_user(self.user_id)
        
        if not user:
            return {
                'answer': 'Пользователь не найден. Пожалуйста, авторизуйтесь.',
                'intent': 'error',
                'confidence': 0
            }
        
        # Формируем контекст пользователя
        user_context = {
            'full_name': user.get_full_name() or user.username,
            'status': user.status,
            'region': user.region,
            'income': float(user.total_income) if user.total_income else 0,
        }
        
        # Инициализируем AI сервис
        ai_service = OllamaService()
        
        # Классификация вопроса
        intent_result = ai_service.classify_intent(question)
        
        # Поиск в БЗ
        context_docs = ai_service.search_knowledge_base(question)
        
        # Генерация ответа
        start_time = time.time()
        response = ai_service.generate_response(
            question,
            user_context,
            context_docs
        )
        response_time = time.time() - start_time
        
        # Сохраняем в БД
        chat = await self.save_chat_history(
            user=user,
            question=question,
            answer=response['answer'],
            intent=intent_result['intent'],
            confidence=intent_result['confidence'],
            tokens_used=response.get('tokens', 0),
            response_time=response_time,
            context=user_context
        )
        
        return {
            'id': chat.id,
            'question': question,
            'answer': response['answer'],
            'intent': intent_result['intent'],
            'confidence': intent_result['confidence'],
            'response_time': response_time,
            'documents_used': len(context_docs)
        }
    
    async def send_answer(self, answer_data):
        """Отправка ответа клиенту"""
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'content': answer_data['answer'],
            'metadata': {
                'id': answer_data.get('id'),
                'intent': answer_data.get('intent'),
                'confidence': answer_data.get('confidence'),
                'response_time': answer_data.get('response_time'),
                'documents_used': answer_data.get('documents_used', 0)
            },
            'timestamp': time.time()
        }))
    
    async def send_typing(self, is_typing):
        """Отправка индикатора печатания"""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'is_typing': is_typing,
            'timestamp': time.time()
        }))
    
    async def send_error(self, error_message):
        """Отправка сообщения об ошибке"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'content': error_message,
            'timestamp': time.time()
        }))
    
    @database_sync_to_async
    def get_user(self, user_id):
        """Получение пользователя из БД"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def save_chat_history(self, **kwargs):
        """Сохранение истории чата в БД"""
        from chat.models import ChatHistory
        return ChatHistory.objects.create(**kwargs)
