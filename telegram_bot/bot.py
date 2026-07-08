"""
Telegram бот для платформенной занятости
"""
import os
import sys
import django
import logging
import re
from dotenv import load_dotenv
from asgiref.sync import sync_to_async

# Загрузка переменных окружения
load_dotenv()

# Настройка Django окружения
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import time

from users.models import User
from chat.models import ChatHistory
from core.ollama_service import OllamaService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_markdown(text):
    """
    Очищает текст от проблемных Markdown символов.
    """
    # Удаляем незакрытые теги жирного текста
    text = re.sub(r'\*\*([^*]+)$', r'\1', text)
    text = re.sub(r'^([^*]+)\*\*', r'\1', text)
    
    # Экранируем специальные символы
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        if char in text:
            # Проверяем, не является ли символ частью тега
            text = text.replace(char, f'\\{char}')
    
    return text


class DriveCoreTelegramBot:
    """Telegram бот для платформенной занятости"""
    
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env")
        
        logger.info(f"Токен загружен: {self.token[:10]}...")
        
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()
        logger.info("Telegram бот инициализирован")
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.app.add_handler(CommandHandler("start", self.start_handler))
        self.app.add_handler(CommandHandler("help", self.help_handler))
        self.app.add_handler(CommandHandler("status", self.status_handler))
        self.app.add_handler(CommandHandler("tax", self.tax_handler))
        self.app.add_handler(CallbackQueryHandler(self.callback_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        self.app.add_error_handler(self.error_handler)
    
    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start - регистрация пользователя"""
        user = update.effective_user
        
        keyboard = [
            [InlineKeyboardButton("Я водитель", callback_data="role_driver")],
            [InlineKeyboardButton("Я из команды", callback_data="role_team")],
            [InlineKeyboardButton("Госорганы", callback_data="role_gov")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Привет, {user.first_name}!\n\n"
            "Я - DriveCore, ИИ-ассистент для платформенной занятости.\n\n"
            "Я помогу тебе:\n"
            "• Разобраться с налогами \n"
            "• Оформить документы \n"
            "• Узнать о выплатах \n"
            "• Получить поддержку \n\n"
            "Выбери свою роль:",
            reply_markup=reply_markup
        )
    
    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help - помощь"""
        help_text = """
Доступные команды:

/start - Начать работу (регистрация)
/help - Показать эту справку
/status - Мой статус
/tax - Налоговый калькулятор

Как задать вопрос:
Просто напиши мне любое сообщение!

Примеры вопросов:
• "Как получить разрешение на такси?"
• "Сколько налогов нужно платить?"
• "Что делать, если превысил лимит?"

Веб-версия: http://localhost:8000
        """
        await update.message.reply_text(help_text)
    
    async def status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status - статус пользователя"""
        telegram_id = str(update.effective_user.id)
        
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            
            status_text = f"""
Мой статус

Имя: {user.get_full_name() or user.username}
Роль: {user.get_role_display()}
Статус: {user.get_status_display()}
Регион: {user.region}
Доход: {user.total_income:,.0f} ₽
Налоговая ставка: {user.tax_rate}%
Документы: {' Проверены' if user.documents_verified else ' Не проверены'}
            """
            await update.message.reply_text(status_text)
            
        except User.DoesNotExist:
            await update.message.reply_text(
                " Вы не зарегистрированы. Используйте /start для регистрации."
            )
    
    async def tax_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /tax - налоговый калькулятор"""
        telegram_id = str(update.effective_user.id)
        
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            income = float(user.total_income) if user.total_income else 100000
            
            tax_rates = {
                'self_employed': 4.0,
                'ie': 6.0,
                'employee': 13.0
            }
            rate = tax_rates.get(user.status, 4.0)
            tax = income * (rate / 100)
            
            response = f"""
Налоговый расчет

Статус: {user.get_status_display()}
Доход: {income:,.0f} ₽
Ставка: {rate}%
Налог: {tax:,.0f} ₽
Чистый доход: {income - tax:,.0f} ₽

Для точного расчета используйте веб-версию.
            """
            await update.message.reply_text(response)
            
        except User.DoesNotExist:
            await update.message.reply_text(
                "Вы не зарегистрированы. Используйте /start для регистрации."
            )
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на инлайн-кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        telegram_id = str(update.effective_user.id)
        
        if data.startswith("role_"):
            role = data.replace("role_", "")
            context.user_data['role'] = role
            
            status_keyboard = [
                [InlineKeyboardButton("Самозанятый", callback_data="status_self_employed")],
                [InlineKeyboardButton("Индивидуальный предприниматель", callback_data="status_ie")],
                [InlineKeyboardButton("Наёмный работник", callback_data="status_employee")]
            ]
            
            await query.edit_message_text(
                f"Роль выбрана: {role}\n\nТеперь укажи свой статус:",
                reply_markup=InlineKeyboardMarkup(status_keyboard)
            )
        
        elif data.startswith("status_"):
            status = data.replace("status_", "")
            context.user_data['status'] = status
            
            user_info = update.effective_user
            
            user = await self.create_or_update_user(
                telegram_id=telegram_id,
                username=user_info.username or f"user_{telegram_id[:8]}",
                first_name=user_info.first_name or '',
                last_name=user_info.last_name or '',
                role=context.user_data.get('role', 'driver'),
                status=status
            )
            
            await query.edit_message_text(
                f"Статус сохранён: {status}\n\n"
                "Теперь ты можешь задавать мне вопросы!\n\n"
                "Просто напиши что-нибудь, и я помогу."
            )
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        telegram_id = str(update.effective_user.id)
        question = update.message.text
        
        await update.message.chat.send_action(action="typing")
        
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            
            if not user:
                await update.message.reply_text(
                    "Пожалуйста, сначала используйте команду /start для регистрации."
                )
                return
            
            user_context = {
                'full_name': user.get_full_name() or user.username,
                'status': user.status,
                'region': user.region,
                'income': float(user.total_income) if user.total_income else 0,
            }
            
            ai_service = OllamaService()
            context_docs = ai_service.search_knowledge_base(question)
            intent_result = ai_service.classify_intent(question)
            
            start_time = time.time()
            response = ai_service.generate_response(question, user_context, context_docs)
            response_time = time.time() - start_time
            
            await self.save_chat_history(
                user=user,
                question=question,
                answer=response['answer'],
                intent=intent_result['intent'],
                confidence=intent_result['confidence'],
                tokens_used=response.get('tokens', 0),
                response_time=response_time,
                context=user_context
            )
            
            answer = response['answer']
            # Отправляем без Markdown (plain text)
            if len(answer) > 4000:
                parts = [answer[i:i+4000] for i in range(0, len(answer), 4000)]
                for part in parts:
                    await update.message.reply_text(part)
            else:
                await update.message.reply_text(answer)
                
        except User.DoesNotExist:
            await update.message.reply_text(
                "Пожалуйста, сначала используйте команду /start для регистрации."
            )
        except Exception as e:
            logger.error(f"Error in message_handler: {e}")
            await update.message.reply_text(
                "Произошла ошибка. Попробуйте позже."
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ошибок"""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Произошла ошибка. Попробуйте позже."
            )
    
    @sync_to_async
    def get_user_by_telegram_id(self, telegram_id):
        return User.objects.get(telegram_id=telegram_id)
    
    @sync_to_async
    def create_or_update_user(self, telegram_id, username, first_name, last_name, role, status):
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'status': status,
            }
        )
        if created:
            logger.info(f"Новый пользователь: {user.username}")
        return user
    
    @sync_to_async
    def save_chat_history(self, **kwargs):
        return ChatHistory.objects.create(**kwargs)
    
    def run(self):
        """Запуск бота"""
        print("=" * 50)
        print("Telegram бот запущен...")
        print("Найдите бота в Telegram и нажмите /start")
        print("Для остановки нажмите Ctrl+C")
        print("=" * 50)
        self.app.run_polling()


if __name__ == "__main__":
    try:
        bot = DriveCoreTelegramBot()
        bot.run()
    except ValueError as e:
        print(f"\nОшибка: {e}")
