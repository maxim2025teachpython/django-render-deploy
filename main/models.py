from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField("zagpolovok",max_length=100)
    text = models.TextField()
    author = models.CharField("avtor",max_length=100)
    date = models.DateField()

    class Meta:
        verbose_name = "zapis"
        verbose_name_plural = "zapisi"

    def __str__(self):
        return self.title , self.text, self.author # Только заголовок