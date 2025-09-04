from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import Post
from .ai_assistant import get_ai_assistant

class PostGenerationForm(forms.ModelForm):
    topic = forms.CharField(
        required=False,
        help_text="Введите тему для генерации поста. Если заполнено — пост будет создан ИИ автоматически.",
        label="Тема для ИИ"
    )

    class Meta:
        model = Post
        fields = '__all__'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostGenerationForm

    list_display = ('title', 'author', 'is_ai_generated', 'ai_sentiment', 'razdel', 'date')
    list_filter = ('is_ai_generated', 'ai_sentiment', 'razdel')
    search_fields = ('title', 'text', 'author', 'razdel')

    def save_model(self, request, obj, form, change):
        topic = form.cleaned_data.get('topic')
        if topic and not change:
            ai = get_ai_assistant()
            generated = ai.generate_full_post(topic)
            obj.title = generated['title']
            obj.text = generated['text']
            obj.razdel = generated['razdel']
            obj.author = "ИИ-генератор"
            obj.date = timezone.now().date()
            obj.is_ai_generated = True
            obj.ai_sentiment = generated['sentiment']
        super().save_model(request, obj, form, change)
