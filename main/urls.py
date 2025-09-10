# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostView.as_view(), name='posts'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),

    path('', views.home, name='home'),
    path('heroes/', views.heroes, name='heroes'),
    path('items/', views.items, name='items'),
    path('guides/', views.guides, name='guides'),
    path('counters/', views.counters, name='counters'),
]