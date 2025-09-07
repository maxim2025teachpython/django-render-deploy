import requests
import json
import logging
from decouple import config

logger = logging.getLogger(__name__)


class SimpleAIAssistant:
    """Простой ИИ помощник, работающий через API"""

    def __init__(self):
        self.api_key = config('OPENAI_API_KEY', default=None)
        self.available = self.api_key is not None

    def is_available(self):
        """Проверка доступности ИИ"""
        return self.available

    def chat(self, message):
        """Получить ответ от ИИ"""
        if not self.is_available():
            return "ИИ временно недоступен. Добавьте OPENAI_API_KEY в настройки."

        try:
            # Простые ответы без API для демонстрации
            responses = {
                'привет': 'Привет! Как дела?',
                'как дела': 'У меня всё отлично! А как у вас?',
                'что умеешь': 'Я могу отвечать на вопросы, помогать с текстами и общаться!',
                'спасибо': 'Пожалуйста! Рад помочь!',
                'пока': 'До свидания! Было приятно пообщаться!'
            }

            message_lower = message.lower().strip()

            # Поиск точного совпадения
            for key, response in responses.items():
                if key in message_lower:
                    return response

            # Если нет API ключа, возвращаем простой ответ
            if not self.api_key:
                return f"Интересный вопрос: '{message}'. К сожалению, для полноценной работы нужен API ключ."

            # Здесь может быть вызов к реальному API
            return self._call_openai_api(message)

        except Exception as e:
            logger.error(f"Ошибка в чате с ИИ: {e}")
            return "Произошла ошибка при обращении к ИИ. Попробуйте позже."

    def _call_openai_api(self, message):
        """Вызов OpenAI API (если есть ключ)"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'user', 'content': message}
                ],
                'max_tokens': 150,
                'temperature': 0.7
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"OpenAI API error: {response.status_code}")
                return "Не удалось получить ответ от ИИ сервиса."

        except requests.exceptions.Timeout:
            return "Превышено время ожидания ответа от ИИ."
        except Exception as e:
            logger.error(f"Ошибка OpenAI API: {e}")
            return "Ошибка при обращении к ИИ сервису."


# Глобальный экземпляр
_ai_assistant = None


def get_ai_assistant():
    """Получить экземпляр ИИ помощника"""
    global _ai_assistant
    if _ai_assistant is None:
        _ai_assistant = SimpleAIAssistant()
    return _ai_assistant