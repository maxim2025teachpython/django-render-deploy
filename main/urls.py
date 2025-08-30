from django.urls import path
from . import views
from .views import PostView

urlpatterns = [
    path('', PostView.as_view(), name='home'),
]
