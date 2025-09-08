import requests
import json
import logging
from decouple import config

logger = logging.getLogger(__name__)


class SimpleAIAssistant:
    """Простой ИИ помощник, работающий через API"""

    def __init__(self):
        # Сначала пробуем GROQ_API_KEY, потом OPENAI_API_KEY для совместимости
        self.api_key = config('GROQ_API_KEY', default=config('OPENAI_API_KEY', default=None))
        self.available = self.api_key is not None

    def is_available(self):
        """Проверка доступности ИИ"""
        return self.available

    def chat(self, message):
        """Получить ответ от ИИ"""
        if not self.is_available():
            return "ИИ временно недоступен. Добавьте GROQ_API_KEY в настройки."

        try:
            # Простые ответы без API для демонстрации
            responses = {
                'привет': 'Привет! Как дела? 👋',
                'как дела': 'У меня всё отлично! А как у вас?',
                'что умеешь': 'Я могу отвечать на вопросы, помогать с текстами и общаться! Работаю на Llama 3.1 🦙',
                'спасибо': 'Пожалуйста! Рад помочь! 😊',
                'пока': 'До свидания! Было приятно пообщаться! 👋'
            }

            message_lower = message.lower().strip()

            # Поиск точного совпадения
            for key, response in responses.items():
                if key in message_lower:
                    return response

            # Если нет API ключа, возвращаем простой ответ
            if not self.api_key:
                return f"Интересный вопрос: '{message}'. К сожалению, для полноценной работы нужен API ключ."

            # 🔄 ЗДЕСЬ ИЗМЕНЕНИЯ: Вызываем Groq API вместо OpenAI
            return self._call_groq_api(message)

        except Exception as e:
            logger.error(f"Ошибка в чате с ИИ: {e}")
            return "Произошла ошибка при обращении к ИИ. Попробуйте позже."

    def _call_groq_api(self, message):
        """🆕 НОВЫЙ МЕТОД: Вызов Groq API (бесплатно!)"""
        try:
            logger.info(f"Отправляем запрос к Groq API: {message[:50]}...")

            # 🔄 ИЗМЕНЕНИЕ 1: Новые headers для Groq
            headers = {
                'Authorization': f'Bearer {self.api_key}',  # Теперь GROQ_API_KEY
                'Content-Type': 'application/json'
            }

            # 🔄 ИЗМЕНЕНИЕ 2: Новая модель и настройки
            data = {
                'model': 'llama-3.1-8b-instant',  # Вместо gpt-3.5-turbo
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Ты дружелюбный ИИ-помощник. Отвечай кратко и по делу на русском языке.'
                    },
                    {
                        'role': 'user',
                        'content': message
                    }
                ],
                'max_tokens': 150,
                'temperature': 0.7
            }

            # 🔄 ИЗМЕНЕНИЕ 3: Новый URL для Groq
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',  # Вместо OpenAI URL
                headers=headers,
                json=data,
                timeout=30
            )

            logger.info(f"Ответ от Groq: статус {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return "Не удалось получить ответ от ИИ сервиса."

        except requests.exceptions.Timeout:
            return "Превышено время ожидания ответа от ИИ."
        except Exception as e:
            logger.error(f"Ошибка Groq API: {e}")
            return "Ошибка при обращении к ИИ сервису."

    # 🗑️ Этот старый метод можно удалить или оставить как резерв
    def _call_openai_api(self, message):
        """СТАРЫЙ МЕТОД: Вызов OpenAI API (можно удалить)"""
        # ... старый код OpenAI ...
        pass


# Глобальный экземпляр
_ai_assistant = None


def get_ai_assistant():
    """Получить экземпляр ИИ помощника"""
    global _ai_assistant
    if _ai_assistant is None:
        _ai_assistant = SimpleAIAssistant()
    return _ai_assistant