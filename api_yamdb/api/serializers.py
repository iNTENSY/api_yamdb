from django.utils import timezone
from rest_framework import serializers

from reviews.models import Genre, Title, Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if data['year'] > timezone.now().year:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения, которые еще не вышли!'
            )
        return data

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre',)

