from django.urls import path
from .views import PostView, PostDetailView, ai_chat

urlpatterns = [
    path('', PostView.as_view(), name='posts'),
    path('ai_chat/', ai_chat, name='ai_chat'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),  # 👈 вот он
]
