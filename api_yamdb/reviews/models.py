from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

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
    description = models.TextField(max_length=200)

    def __str__(self):
        return self.text


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    score = models.IntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.author.username} on {self.content.title}'


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on Review {self.review.id}'
