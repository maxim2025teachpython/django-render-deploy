from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.db.models import Q
from .models import Post


class PostView(View):
    def get(self, request):
        query = request.GET.get('query', '')
        if query:
            posts = Post.objects.filter(
                Q(title__icontains=query) | Q(text__icontains=query)
            ).order_by('-id')  # Добавлен порядок сортировки
        else:
            posts = Post.objects.all().order_by('-id')  # Добавлен порядок сортировки
        return render(request, 'home.html', {
            'posts_list': posts,
            'query': query
        })

    def post(self, request):
        # Новый метод для добавления постов
        title = request.POST.get('title')
        text = request.POST.get('text')

        if title and text:
            Post.objects.create(title=title, text=text)

        return redirect('posts')  # Замените на имя вашего URL-маршрута