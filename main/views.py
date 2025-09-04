# views.py - Обновленный файл с ИИ функциональностью

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone
import json
import logging

from .models import Post
from .ai_assistant import get_ai_assistant

logger = logging.getLogger(__name__)


class PostView(View):
    """Основное представление для постов с ИИ поддержкой"""

    def get(self, request):
        query = request.GET.get('query', '')
        ai_search = request.GET.get('ai_search', False)

        if query:
            if ai_search:
                # ИИ поиск
                try:
                    ai = get_ai_assistant()
                    if ai.is_available():
                        all_posts = Post.objects.all().order_by('-id')[:50]  # Ограничиваем для ИИ
                        posts_data = [
                            {'title': post.title, 'text': post.text}
                            for post in all_posts
                        ]
                        relevant_indices = ai.intelligent_search(query, posts_data)

                        if relevant_indices:
                            posts_list = list(all_posts)
                            posts = [posts_list[i] for i in relevant_indices if i < len(posts_list)]
                        else:
                            posts = []
                    else:
                        # Fallback на обычный поиск если ИИ недоступен
                        posts = Post.objects.filter(
                            Q(title__icontains=query) | Q(text__icontains=query)
                        ).order_by('-id')

                except Exception as e:
                    logger.error(f"Ошибка ИИ поиска: {e}")
                    # Fallback на обычный поиск
                    posts = Post.objects.filter(
                        Q(title__icontains=query) | Q(text__icontains=query)
                    ).order_by('-id')
            else:
                # Обычный поиск
                posts = Post.objects.filter(
                    Q(title__icontains=query) | Q(text__icontains=query)
                ).order_by('-id')
        else:
            posts = Post.objects.all().order_by('-id')

        return render(request, 'home.html', {
            'posts_list': posts,
            'query': query,
            'ai_search': ai_search,
            'ai_available': get_ai_assistant().is_available()
        })

    def post(self, request):
        """Добавление нового поста с ИИ поддержкой"""
        title = request.POST.get('title')
        text = request.POST.get('text')
        is_ai_generated = request.POST.get('ai_generated', False)

        if title and text:
            try:
                Post.objects.create(
                    title=title,
                    text=text,
                    is_ai_generated=bool(is_ai_generated),
                    created_at=timezone.now()
                )
            except Exception as e:
                logger.error(f"Ошибка создания поста: {e}")

        return redirect('posts')


# ИИ API endpoints

@csrf_exempt
@require_http_methods(["POST"])
def ai_generate_title(request):
    """Генерация заголовка с помощью ИИ"""
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        topic = data.get('topic', '')

        ai = get_ai_assistant()

        if not ai.is_available():
            return JsonResponse({
                'success': False,
                'error': 'ИИ недоступен. Проверьте настройки API ключа.'
            })

        title = ai.generate_post_title(content=content, topic=topic)

        if title:
            return JsonResponse({
                'success': True,
                'title': title
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Не удалось сгенерировать заголовок'
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат данных'
        })
    except Exception as e:
        logger.error(f"Ошибка генерации заголовка: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Произошла ошибка при генерации заголовка'
        })


@csrf_exempt
@require_http_methods(["POST"])
def ai_generate_content(request):
    """Генерация содержания поста с помощью ИИ"""
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '')
        style = data.get('style', 'информативный')
        length = data.get('length', 'средний')

        if not topic:
            return JsonResponse({
                'success': False,
                'error': 'Тема обязательна для генерации контента'
            })

        ai = get_ai_assistant()

        if not ai.is_available():
            return JsonResponse({
                'success': False,
                'error': 'ИИ недоступен. Проверьте настройки API ключа.'
            })

        content = ai.generate_post_content(topic=topic, style=style, length=length)

        if content:
            return JsonResponse({
                'success': True,
                'content': content
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Не удалось сгенерировать контент'
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат данных'
        })
    except Exception as e:
        logger.error(f"Ошибка генерации контента: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Произошла ошибка при генерации контента'
        })


@csrf_exempt
@require_http_methods(["POST"])
def ai_improve_text(request):
    """Улучшение текста с помощью ИИ"""
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        improvement_type = data.get('improvement_type', 'общее')

        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Текст для улучшения не может быть пустым'
            })

        ai = get_ai_assistant()

        if not ai.is_available():
            return JsonResponse({
                'success': False,
                'error': 'ИИ недоступен. Проверьте настройки API ключа.'
            })

        improved_text = ai.improve_text(text=text, improvement_type=improvement_type)

        if improved_text:
            return JsonResponse({
                'success': True,
                'improved_text': improved_text
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Не удалось улучшить текст'
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат данных'
        })
    except Exception as e:
        logger.error(f"Ошибка улучшения текста: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Произошла ошибка при улучшении текста'
        })


@csrf_exempt
@require_http_methods(["POST"])
def ai_analyze_post(request):
    """Анализ поста с помощью ИИ"""
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        text = data.get('text', '')

        if post_id:
            post = get_object_or_404(Post, id=post_id)
            text = post.text

        if not text:
            return JsonResponse({
                'success': False,
                'error': 'Текст для анализа не найден'
            })

        ai = get_ai_assistant()

        if not ai.is_available():
            return JsonResponse({
                'success': False,
                'error': 'ИИ недоступен. Проверьте настройки API ключа.'
            })

        sentiment = ai.analyze_sentiment(text)

        # Дополнительная статистика
        word_count = len(text.split())
        char_count = len(text)

        return JsonResponse({
            'success': True,
            'analysis': {
                'sentiment': sentiment,
                'word_count': word_count,
                'char_count': char_count,
                'estimated_reading_time': max(1, word_count // 200)  # минуты
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат данных'
        })
    except Exception as e:
        logger.error(f"Ошибка анализа поста: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Произошла ошибка при анализе поста'
        })


@csrf_exempt
@require_http_methods(["POST"])
def ai_chat(request):
    """Чат с ИИ"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')

        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Сообщение не может быть пустым'
            })

        ai = get_ai_assistant()

        if not ai.is_available():
            return JsonResponse({
                'success': False,
                'error': 'ИИ недоступен. Проверьте настройки API ключа.'
            })

        response = ai.chat(message)

        if response:
            return JsonResponse({
                'success': True,
                'response': response
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Не удалось получить ответ от ИИ'
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат данных'
        })
    except Exception as e:
        logger.error(f"Ошибка ИИ чата: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Произошла ошибка при общении с ИИ'
        })


@require_http_methods(["GET"])
def ai_generate_ideas(request):
    """Генерация идей для постов"""
    category = request.GET.get('category', 'общие')
    count = int(request.GET.get('count', 5))

    try:
        ai = get_ai_assistant()

        if not ai.is_available():
            return JsonResponse({
                'success': False,
                'error': 'ИИ недоступен. Проверьте настройки API ключа.'
            })

        ideas = ai.generate_post_ideas(category=category, count=count)

        if ideas:
            return JsonResponse({
                'success': True,
                'ideas': ideas
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Не удалось сгенерировать идеи'
            })

    except Exception as e:
        logger.error(f"Ошибка генерации идей: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Произошла ошибка при генерации идей'
        })


@require_http_methods(["GET"])
def ai_status(request):
    """Проверка статуса ИИ"""
    try:
        ai = get_ai_assistant()
        stats = ai.get_usage_stats()

        return JsonResponse({
            'success': True,
            'status': stats
        })

    except Exception as e:
        logger.error(f"Ошибка проверки статуса ИИ: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Ошибка проверки статуса ИИ'
        })


# Вспомогательная функция для совместимости с существующим кодом
def posts_list(request):
    """Функция-обертка для совместимости"""
    return PostView.as_view()(request)