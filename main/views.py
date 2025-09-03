from django.shortcuts import render
from django.views.generic.base import View
from django.db.models import Q
from .models import Post

class PostView(View):
    def get(self, request):
        query = request.GET.get('query', '')
        if query:
            posts = Post.objects.filter(
                Q(title__icontains=query) | Q(text__icontains=query)
            )
        else:
            posts = Post.objects.all()
        return render(request, 'home.html', {
            'posts_list': posts,
            'query': query
        })
