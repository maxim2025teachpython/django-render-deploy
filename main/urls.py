from django.urls import path
from .views import PostView, ai_chat

urlpatterns = [
    path('', PostView.as_view(), name='posts'),       # и GET, и POST
    path('ai_chat/', ai_chat, name='ai_chat'),        # ИИ-чат
]
