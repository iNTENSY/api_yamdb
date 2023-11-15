from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from reviews.models import Genre, Title, Category


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с пользователями.

    Отсутствуют поля сериализатора
    """

    class Meta:
        model = User
        fields = []


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с жанрами.
    """

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с категориями.
    """

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с произведениями.

    Метод validate проверяет, вышло ли поизведение
    """

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre',)

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения, которые еще не вышли!'
            )
        return value
