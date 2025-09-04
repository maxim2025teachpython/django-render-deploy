# models.py - Адаптированная модель с ИИ полями

from django.db import models
from django.utils import timezone


class Post(models.Model):
    title = models.CharField("zagpolovok", max_length=100)
    text = models.TextField("содержание")
    razdel = models.TextField("раздел")
    author = models.CharField("avtor", max_length=100)
    date = models.DateField("дата")

    # Новые поля для ИИ функциональности
    is_ai_generated = models.BooleanField("создано ИИ", default=False)
    ai_sentiment = models.CharField(
        "настроение (ИИ)",
        max_length=20,
        choices=[
            ('позитивное', 'Позитивное'),
            ('негативное', 'Негативное'),
            ('нейтральное', 'Нейтральное')
        ],
        blank=True,
        null=True
    )
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        verbose_name = "zapis"
        verbose_name_plural = "zapisi"
        ordering = ['-created_at', '-date']

    def __str__(self):
        return f'{self.title},{self.author}'

    @property
    def word_count(self):
        """Подсчет количества слов в тексте"""
        return len(self.text.split()) if self.text else 0

    @property
    def estimated_reading_time(self):
        """Приблизительное время чтения в минутах"""
        return max(1, self.word_count // 200)