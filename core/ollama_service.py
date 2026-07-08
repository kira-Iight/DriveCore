"""
Сервис для работы с ИИ через RAG с векторным поиском
"""
import logging
from typing import List, Dict, Any
from django.conf import settings

from core.services.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class OllamaClient:
    """Клиент для работы с Ollama API"""
    
    def __init__(self, model: str = "llama3.2:3b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
    
    def is_available(self) -> bool:
        """Проверяет доступность Ollama"""
        try:
            import requests
            response = requests.get(f"{self.host}/api/version", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 500):
        """Генерирует ответ через Ollama"""
        try:
            import ollama
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": temperature,
                    "top_p": 0.8,
                    "max_tokens": max_tokens
                }
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return None


class OllamaService:
    """
    Главный сервис для генерации ответов через RAG.
    Использует векторный поиск для нахождения релевантных документов.
    """
    
    def __init__(self):
        self.model = getattr(settings, 'OLLAMA_MODEL', 'llama3.2:3b')
        self.host = getattr(settings, 'OLLAMA_HOST', 'http://localhost:11434')
        self.knowledge_base = KnowledgeBase()
        self.llm = OllamaClient(self.model, self.host)
        
        self.system_prompt = """
Ты - ИИ-ассистент "DriveCore" для водителей такси Яндекс Про.

Твоя задача - помогать водителям с вопросами о:
- Налогах и платежах
- Документах и регистрации
- Правилах и законах
- Выплатах и бонусах

Правила:
1. Используй информацию из контекста как основной источник
2. Если в контексте нет информации - скажи об этом честно
3. Не выдумывай факты и цифры
4. Структурируй ответ (списки, пункты)
5. Будь вежливым и профессиональным

Контекст:
{context}

Вопрос пользователя:
{question}
"""
    
    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Поиск в базе знаний с использованием векторов"""
        return self.knowledge_base.search(query, top_k, use_vectors=True)
    
    def classify_intent(self, question: str) -> Dict[str, Any]:
        """Классификация интента вопроса"""
        keywords = {
            'tax': ['налог', 'ставка', 'процент', 'нпд', 'усн', '4%', '6%'],
            'documents': ['документ', 'паспорт', 'регистрация', 'разрешение', 'справка', 'ИП'],
            'payments': ['выплата', 'деньги', 'карта', 'перевод', 'баланс', 'оплата'],
        }
        
        question_lower = question.lower()
        scores = {}
        
        for intent, words in keywords.items():
            score = sum(1 for word in words if word in question_lower)
            scores[intent] = score
        
        max_intent = max(scores, key=scores.get, default='general')
        max_score = scores.get(max_intent, 0)
        
        return {
            'intent': max_intent if max_score > 0 else 'general',
            'confidence': min(max_score / 2, 1.0)
        }
    
    def _build_prompt(self, question: str, documents: List[Dict[str, Any]]) -> str:
        """Строит промпт для LLM"""
        if not documents:
            context = "Информация в базе знаний отсутствует."
        else:
            context = "\n\n".join([
                f" {doc['title']}\n{doc['content']}"
                for doc in documents[:3]
            ])
            
            search_type = documents[0].get('search_type', 'unknown')
            context += f"\n\n[Найдено через: {search_type} поиск]"
        
        return self.system_prompt.format(
            context=context,
            question=question
        )
    
    def generate_response(
        self, 
        question: str, 
        user_context: Dict[str, Any], 
        context_docs: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Генерация ответа с использованием RAG"""
        
        # Если документы не переданы - ищем
        if context_docs is None:
            context_docs = self.search_knowledge_base(question)
        
        # Строим промпт
        prompt = self._build_prompt(question, context_docs)
        
        # Пробуем сгенерировать через LLM
        if self.llm.is_available():
            answer = self.llm.generate(prompt)
            if answer:
                return {
                    'answer': answer,
                    'tokens': 0,
                    'model': self.model,
                    'source': 'ollama_with_rag',
                    'documents_used': len(context_docs)
                }
        
        # Если LLM недоступен - возвращаем контекст как ответ
        if context_docs:
            return {
                'answer': self._format_documents_as_answer(context_docs, question),
                'tokens': 0,
                'model': 'knowledge_base',
                'source': 'knowledge_base',
                'documents_used': len(context_docs)
            }
        
        # Если ничего не работает - fallback
        return {
            'answer': self._get_fallback_response(question),
            'tokens': 0,
            'model': 'fallback',
            'source': 'fallback',
            'documents_used': 0
        }
    
    def _format_documents_as_answer(self, documents: List[Dict[str, Any]], question: str) -> str:
        """Форматирует документы как ответ"""
        response = " Информация по вашему вопросу:\n\n"
        
        for doc in documents[:3]:
            response += f" {doc['title']}\n\n{doc['content']}\n\n"
        
        response += " Если вам нужна более подробная информация, уточните вопрос."
        return response
    
    def _get_fallback_response(self, question: str) -> str:
        """Ответ по умолчанию"""
        return """
Информация не найдена

Я не могу найти точную информацию по вашему вопросу.

Рекомендации:
• Уточните вопрос, используя более конкретные слова
• Проверьте, есть ли информация в базе знаний
• Или обратитесь в поддержку Яндекс Про

Вопросы, на которые я могу ответить:
• О налогах (ставки, лимиты, расчеты)
• О документах (разрешения, регистрация)
• О выплатах (карта, переводы)
• Об открытии ИП
"""
    
    def get_stats(self) -> Dict[str, Any]:
        """Статистика сервиса"""
        kb_stats = self.knowledge_base.get_stats()
        return {
            **kb_stats,
            'ollama_available': self.llm.is_available(),
            'model': self.model
        }
