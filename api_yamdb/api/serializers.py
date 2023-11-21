from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from reviews.models import Title, Category, Genre, Review, Comment


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с пользователями.
    """

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с запросами по .../auth/signup/
    Принимает два поля username, email.
    """
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        required=True
    )
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ['username', 'email']

    def validate(self, attrs):
        if attrs['username'] == 'me':
            raise ValidationError('Invalid username: `me`!')

        try:
            User.objects.get_or_create(
                email=attrs['email'],
                username=attrs['username']
            )
        except IntegrityError:
            raise ValidationError(detail='Invalid request data!')
        return attrs


class TokenSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'confirmation_code']

    def validate_username(self, value):
        get_object_or_404(User, username=value)
        return value


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


class TitleListingField(serializers.SlugRelatedField):
    """
    Кастомное поле для правильного отображения жанров и категорий.
    """
    def to_representation(self, value):
        return {'name': value.name, 'slug': value.slug}


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с произведениями.

    Метод validate проверяет, вышло ли поизведение
    """
    rating = serializers.FloatField(read_only=True)

    category = TitleListingField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = TitleListingField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                'Название не может быть длиннее 256 символов!'
            )
        return value

    def validate_year(self, value):
        if value > timezone.now().year:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения, которые еще не вышли!'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    '''Сериалайзер отзывов.'''
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('title', 'author')

    def validate(self, data):
        if Review.objects.filter(
            author=self.context['request'].user,
            title_id=self.context['view'].kwargs.get('title_id')
        ).exists() and self.context['request'].method == 'POST':
            raise serializers.ValidationError(
                'Нельзя оставить два отзыва на одно произведение.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    '''Сериалайзер комментариев.'''
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('review', 'author')
