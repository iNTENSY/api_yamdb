from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_legth=50, unique=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_legth=50, unique=True)

    def __str__(self):
        return self.title


class Title(models.Model):
    name = models.TextField(max_length=200)
    year = models.DateField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category'
    )
    genre = models.ManyToManyField(Genre, blank=True)

    def __str__(self):
        return self.text
