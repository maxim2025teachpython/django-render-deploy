from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.utils import timezone
import json
import logging

from .models import Post
from .ai_assistant import get_ai_assistant
from django.views.generic import DetailView

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'


class PostView(View):
    """Главная страница блога: отображение и добавление постов"""

    def get(self, request):
        # Поддерживаем оба параметра для совместимости
        search_query = request.GET.get('query', '') or request.GET.get('search', '')
        ai_search = request.GET.get('ai_search', False)

        if search_query:
            posts = Post.objects.filter(
                Q(title__icontains=search_query) | Q(text__icontains=search_query)
            ).order_by('-created_at')
        else:
            posts = Post.objects.all().order_by('-created_at')

        # Проверяем доступность ИИ
        try:
            ai_assistant = get_ai_assistant()
            ai_available = ai_assistant.is_available()
        except Exception as e:
            logger.error(f"Ошибка при проверке доступности ИИ: {e}")
            ai_available = False

        return render(request, 'home.html', {
            'posts_list': posts,
            'search_query': search_query,  # Переименовал для ясности
            'ai_search': ai_search,
            'ai_available': ai_available
        })

    def post(self, request):
        title = request.POST.get('title')
        text = request.POST.get('text')

        if title and text:
            try:
                Post.objects.create(
                    title=title,
                    text=text,
                    created_at=timezone.now()
                )
                logger.info(f"Создан новый пост: {title}")
            except Exception as e:
                logger.error(f"Ошибка при добавлении поста: {e}")

        return redirect('posts')


@csrf_exempt
def ai_chat(request):
    """Обработка запроса к ИИ-чату"""
    if request.method == 'POST':
        try:
            # Добавляем проверку Content-Type
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Fallback для form data
                data = {'message': request.POST.get('message', '')}

            message = data.get('message', '').strip()

            if not message:
                return JsonResponse({
                    'success': False,
                    'error': 'Сообщение не может быть пустым'
                })

            # Проверяем доступность ИИ
            try:
                ai = get_ai_assistant()
                if not ai.is_available():
                    return JsonResponse({
                        'success': False,
                        'error': 'ИИ временно недоступен. Попробуйте позже.'
                    })
            except Exception as e:
                logger.error(f"Ошибка инициализации ИИ: {e}")
                return JsonResponse({
                    'success': False,
                    'error': 'ИИ недоступен из-за технической ошибки'
                })

            # Получаем ответ от ИИ
            try:
                response = ai.chat(message)
                logger.info(f"ИИ ответил на сообщение: {message[:50]}...")
                return JsonResponse({
                    'success': True,
                    'response': response
                })
            except Exception as e:
                logger.error(f"Ошибка при получении ответа от ИИ: {e}")
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
            logger.error(f"Общая ошибка ИИ-чата: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Произошла непредвиденная ошибка'
            })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Поддерживается только POST запрос'
        })

    '''divide on the main page'''


def heroes(request):
    return render(request, 'heroes.html')


def items(request):
    return render(request, 'items.html')


def guides(request):
    return render(request, 'guides.html')


def counters(request):
    return render(request, 'counters.html')
