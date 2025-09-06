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


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'




class PostView(View):
    """Главная страница блога: отображение и добавление постов"""

    def get(self, request):
        query = request.GET.get('query', '')
        ai_search = request.GET.get('ai_search', False)

        if query:
            posts = Post.objects.filter(
                Q(title__icontains=query) | Q(text__icontains=query)
            ).order_by('-created_at')
        else:
            posts = Post.objects.all().order_by('-created_at')

        return render(request, 'home.html', {
            'posts_list': posts,
            'query': query,
            'ai_search': ai_search,
            'ai_available': get_ai_assistant().is_available()
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
            except Exception as e:
                logger.error(f"Ошибка при добавлении поста: {e}")

        return redirect('posts')


@csrf_exempt
def ai_chat(request):
    """Обработка запроса к ИИ-чату"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')

            if not message:
                return JsonResponse({'success': False, 'error': 'Сообщение не может быть пустым'})

            ai = get_ai_assistant()
            if not ai.is_available():
                return JsonResponse({'success': False, 'error': 'ИИ недоступен'})

            response = ai.chat(message)
            return JsonResponse({'success': True, 'response': response})

        except Exception as e:
            logger.error(f"Ошибка ИИ-чата: {e}")
            return JsonResponse({'success': False, 'error': 'Ошибка при обработке запроса'})
    else:
        return JsonResponse({'success': False, 'error': 'Метод не поддерживается'})
