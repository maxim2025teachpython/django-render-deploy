# urls.py
from django.urls import path
from .views import PostView

urlpatterns = [
    path('', PostView.as_view(), name='posts'),
    path('add/', PostView.as_view(), name='add_post'),  # Для обработки POST
]