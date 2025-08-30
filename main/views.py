from django.shortcuts import render
from django.views.generic.base import View
from .models import Post

class PostView(View):

    def get(self,request):
        posts = Post.objects.all()
        return render(request, 'home.html', {'posts_list':posts})
