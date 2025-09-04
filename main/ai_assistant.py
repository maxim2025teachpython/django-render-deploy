# ai_assistant.py - ИИ модуль для Django сайта постов

import os
import json
import requests
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAssistant:
    """
    ИИ помощник для сайта с постами
    Поддерживает различные API: OpenAI, Anthropic, местные модели
    """

    def __init__(self, api_type='openai'):
        """
        Инициализация ИИ помощника

        Args:
            api_type (str): Тип API ('openai', 'anthropic', 'local')
        """
        self.api_type = api_type
        self.api_key = os.getenv('AI_API_KEY')
        self.chat_history = []

        # Настройки для разных API
        self.api_configs = {
            'openai': {
                'base_url': 'https://api.openai.com/v1',
                'model': 'gpt-3.5-turbo',
                'headers': {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            },
            'anthropic': {
                'base_url': 'https://api.anthropic.com/v1',
                'model': 'claude-3-sonnet-20240229',
                'headers': {
                    'Content-Type': 'application/json',
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01'
                }
            },
            'local': {
                'base_url': 'http://localhost:11434/api',  # Ollama
                'model': 'llama2',
                'headers': {'Content-Type': 'application/json'}
            }
        }

        self.config = self.api_configs.get(api_type, self.api_configs['openai'])
        logger.info(f"ИИ помощник инициализирован с API: {api_type}")

    def is_available(self) -> bool:
        """Проверка доступности ИИ"""
        if self.api_type == 'local':
            return True  # Локальные модели не требуют ключа
        return bool(self.api_key)

    def _make_request(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """
        Универсальный метод для запросов к ИИ API

        Args:
            messages (List[Dict]): Список сообщений для ИИ
            **kwargs: Дополнительные параметры

        Returns:
            Optional[str]: Ответ ИИ или None при ошибке
        """
        if not self.is_available() and self.api_type != 'local':
            logger.error("ИИ недоступен: отсутствует API ключ")
            return None

        try:
            # Подготовка запроса в зависимости от типа API
            if self.api_type == 'openai':
                return self._openai_request(messages, **kwargs)
            elif self.api_type == 'anthropic':
                return self._anthropic_request(messages, **kwargs)
            elif self.api_type == 'local':
                return self._local_request(messages, **kwargs)
            else:
                logger.error(f"Неподдерживаемый тип API: {self.api_type}")
                return None

        except Exception as e:
            logger.error(f"Ошибка запроса к ИИ: {str(e)}")
            return None

    def _openai_request(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """Запрос к OpenAI API"""
        payload = {
            'model': kwargs.get('model', self.config['model']),
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', 1000),
            'temperature': kwargs.get('temperature', 0.7)
        }

        response = requests.post(
            f"{self.config['base_url']}/chat/completions",
            headers=self.config['headers'],
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            logger.error(f"OpenAI API ошибка: {response.status_code}")
            return None

    def _anthropic_request(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """Запрос к Anthropic API"""
        # Anthropic использует другой формат
        system_message = ""
        user_messages = []

        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                user_messages.append(msg)

        payload = {
            'model': kwargs.get('model', self.config['model']),
            'max_tokens': kwargs.get('max_tokens', 1000),
            'messages': user_messages
        }

        if system_message:
            payload['system'] = system_message

        response = requests.post(
            f"{self.config['base_url']}/messages",
            headers=self.config['headers'],
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['content'][0]['text']
        else:
            logger.error(f"Anthropic API ошибка: {response.status_code}")
            return None

    def _local_request(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """Запрос к локальной модели (Ollama)"""
        # Объединяем сообщения в один промт
        prompt = ""
        for msg in messages:
            if msg['role'] == 'system':
                prompt += f"Система: {msg['content']}\n"
            elif msg['role'] == 'user':
                prompt += f"Пользователь: {msg['content']}\n"
            elif msg['role'] == 'assistant':
                prompt += f"Ассистент: {msg['content']}\n"

        payload = {
            'model': kwargs.get('model', self.config['model']),
            'prompt': prompt,
            'stream': False
        }

        response = requests.post(
            f"{self.config['base_url']}/generate",
            headers=self.config['headers'],
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()['response']
        else:
            logger.error(f"Локальная модель ошибка: {response.status_code}")
            return None

    def generate_post_title(self, content: str = "", topic: str = "") -> Optional[str]:
        """
        Генерация заголовка для поста

        Args:
            content (str): Содержание поста
            topic (str): Тема поста

        Returns:
            Optional[str]: Сгенерированный заголовок
        """
        messages = [
            {
                "role": "system",
                "content": "Ты помощник для создания заголовков постов. Создавай краткие, привлекательные заголовки на русском языке длиной не более 100 символов."
            },
            {
                "role": "user",
                "content": f"Создай привлекательный заголовок для поста{f' на тему: {topic}' if topic else ''}{f'. Содержание: {content[:200]}...' if content else ''}"
            }
        ]

        result = self._make_request(messages, max_tokens=100)
        if result:
            # Очищаем заголовок от лишних символов
            title = re.sub(r'^["\']|["\']$', '', result.strip())
            return title[:100]  # Ограничиваем длину
        return None

    def generate_post_content(self, topic: str, style: str = "информативный", length: str = "средний") -> Optional[str]:
        """
        Генерация содержания поста

        Args:
            topic (str): Тема поста
            style (str): Стиль написания
            length (str): Длина поста

        Returns:
            Optional[str]: Сгенерированный контент
        """
        length_map = {
            "короткий": "в 2-3 предложения",
            "средний": "в 1-2 абзаца",
            "длинный": "в 3-4 абзаца"
        }

        messages = [
            {
                "role": "system",
                "content": f"Ты помощник для создания постов в социальных сетях. Пиши {style} посты на русском языке."
            },
            {
                "role": "user",
                "content": f"Напиши {style} пост {length_map.get(length, 'в 1-2 абзаца')} на тему: {topic}"
            }
        ]

        return self._make_request(messages, max_tokens=800)

    def improve_text(self, text: str, improvement_type: str = "общее") -> Optional[str]:
        """
        Улучшение существующего текста

        Args:
            text (str): Исходный текст
            improvement_type (str): Тип улучшения

        Returns:
            Optional[str]: Улучшенный текст
        """
        improvements = {
            "общее": "улучши этот текст, сделай его более читаемым и интересным",
            "грамматика": "исправь грамматические ошибки и улучши стилистику",
            "сократить": "сократи этот текст, оставив главное",
            "расширить": "расширь этот текст, добавив больше деталей",
            "тональность": "сделай тон текста более позитивным и дружелюбным"
        }

        messages = [
            {
                "role": "system",
                "content": "Ты редактор текстов. Улучшай тексты, сохраняя их смысл и стиль автора."
            },
            {
                "role": "user",
                "content": f"{improvements.get(improvement_type, improvements['общее'])}: \"{text}\""
            }
        ]

        return self._make_request(messages, max_tokens=1000)

    def analyze_sentiment(self, text: str) -> str:
        """
        Анализ настроения текста

        Args:
            text (str): Текст для анализа

        Returns:
            str: Настроение ('позитивное', 'негативное', 'нейтральное')
        """
        messages = [
            {
                "role": "system",
                "content": "Проанализируй настроение текста. Отвечай только одним словом: 'позитивное', 'негативное' или 'нейтральное'."
            },
            {
                "role": "user",
                "content": f"Определи настроение этого текста: \"{text}\""
            }
        ]

        result = self._make_request(messages, max_tokens=50, temperature=0.1)
        if result:
            sentiment = result.lower().strip()
            if 'позитив' in sentiment:
                return 'позитивное'
            elif 'негатив' in sentiment:
                return 'негативное'
            else:
                return 'нейтральное'
        return 'нейтральное'

    def intelligent_search(self, query: str, posts: List[Dict]) -> List[int]:
        """
        Умный поиск по постам с помощью ИИ

        Args:
            query (str): Поисковый запрос
            posts (List[Dict]): Список постов для поиска

        Returns:
            List[int]: Индексы релевантных постов
        """
        if not posts:
            return []

        # Ограничиваем количество постов для анализа
        posts_sample = posts[:20]
        posts_text = ""
        for i, post in enumerate(posts_sample):
            posts_text += f"{i}. Заголовок: {post.get('title', '')}\nТекст: {post.get('text', '')[:200]}...\n\n"

        messages = [
            {
                "role": "system",
                "content": "Ты поисковый помощник. Найди наиболее релевантные посты по запросу пользователя. Верни только номера постов через запятую (например: 1, 5, 8)."
            },
            {
                "role": "user",
                "content": f"Запрос: \"{query}\"\n\nПосты:\n{posts_text}\n\nКакие посты наиболее релевантны запросу?"
            }
        ]

        result = self._make_request(messages, max_tokens=100, temperature=0.1)
        if result:
            # Извлекаем номера из ответа
            indices = re.findall(r'\d+', result)
            return [int(i) for i in indices if int(i) < len(posts_sample)]
        return []

    def generate_post_ideas(self, category: str = "общие", count: int = 5) -> List[str]:
        """
        Генерация идей для постов

        Args:
            category (str): Категория идей
            count (int): Количество идей

        Returns:
            List[str]: Список идей
        """
        messages = [
            {
                "role": "system",
                "content": "Ты генератор идей для постов в социальных сетях. Создавай интересные и актуальные темы."
            },
            {
                "role": "user",
                "content": f"Предложи {count} идей для постов в категории \"{category}\". Каждую идею пиши с новой строки, без нумерации."
            }
        ]

        result = self._make_request(messages, max_tokens=500)
        if result:
            ideas = [line.strip() for line in result.split('\n') if line.strip()]
            return ideas[:count]
        return []

    def chat(self, message: str) -> Optional[str]:
        """
        Чат с ИИ помощником

        Args:
            message (str): Сообщение пользователя

        Returns:
            Optional[str]: Ответ ИИ
        """
        # Добавляем сообщение в историю
        self.chat_history.append({"role": "user", "content": message})

        # Ограничиваем историю последними 10 сообщениями
        recent_history = self.chat_history[-10:]

        messages = [
                       {
                           "role": "system",
                           "content": "Ты дружелюбный ИИ помощник для сайта с постами. Помогай с созданием контента, отвечай на вопросы и общайся на русском языке. Будь кратким и полезным."
                       }
                   ] + recent_history

        response = self._make_request(messages, max_tokens=500)

        if response:
            # Добавляем ответ в историю
            self.chat_history.append({"role": "assistant", "content": response})

        return response

    def clear_chat_history(self):
        """Очистка истории чата"""
        self.chat_history = []
        logger.info("История чата очищена")

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Получение статистики использования

        Returns:
            Dict: Статистика
        """
        return {
            "api_type": self.api_type,
            "is_available": self.is_available(),
            "chat_history_length": len(self.chat_history),
            "model": self.config["model"]
        }


# Утилитарные функции для Django views

def get_ai_assistant() -> AIAssistant:
    """Получение экземпляра ИИ помощника"""
    # Можно сделать синглтон или использовать настройки Django
    api_type = os.getenv('AI_API_TYPE', 'openai')
    return AIAssistant(api_type=api_type)


def process_post_with_ai(post_data: Dict, action: str) -> Dict:
    """
    Обработка поста с помощью ИИ

    Args:
        post_data (Dict): Данные поста
        action (str): Действие ('generate_title', 'improve_content', 'analyze')

    Returns:
        Dict: Результат обработки
    """
    ai = get_ai_assistant()
    result = {"success": False, "data": None, "error": None}

    try:
        if action == 'generate_title':
            title = ai.generate_post_title(
                content=post_data.get('content', ''),
                topic=post_data.get('topic', '')
            )
            result["data"] = {"title": title}
            result["success"] = True

        elif action == 'improve_content':
            improved = ai.improve_text(
                text=post_data.get('content', ''),
                improvement_type=post_data.get('improvement_type', 'общее')
            )
            result["data"] = {"improved_content": improved}
            result["success"] = True

        elif action == 'analyze':
            sentiment = ai.analyze_sentiment(post_data.get('content', ''))
            result["data"] = {"sentiment": sentiment}
            result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Ошибка обработки поста с ИИ: {e}")

    return result