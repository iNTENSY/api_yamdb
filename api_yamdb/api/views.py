from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.views import APIView

from reviews.models import Genre, Category, Title

from .serializers import (UserSerializer, GenreSerializer,
                          CategorySerializer, TitleSerializer)
from .permissions import IsAdminOrReadOnly


User = get_user_model()


class SignUpAPIView(APIView):
    """
    Пользователь отправляет POST-запрос с параметрами
    email и username на эндпоинт. Сервис YaMDB отправляет
    письмо с кодом подтверждения (confirmation_code) на указанный адрес email.

    В конечном итоге должно формироваться и отправляться письмо.
    """

    def post(self, *args, **kwargs):
        pass


class TokenAPIView(APIView):
    """
    Пользователь отправляет POST-запрос с
    параметрами username и confirmation_code на эндпоинт,
    в ответе на запрос ему приходит token (JWT-токен).
    """

    def post(self, *args, **kwargs):
        pass


class UserViewSet(viewsets.ModelViewSet):
    """
    Класс позволяет манипулировать моделью User
    исключительно администратором.

    Доступен путь ".../me/" для авторизованного
    пользователя (GET, PATCH запросы).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(methods=['GET', 'PATCH'],
            detail=False,
            url_path='me/',
            permission_classes=[permissions.IsAuthenticated])
    def me(self):
        pass


class GenreViewSet(viewsets.ModelViewSet):
    """
    Класс позволяет просматривать модель Genre
    всем пользователям.

    Манипуляции с моделью Genre разрешены
    исключительно администратору.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    search_fields = ('genre__name')


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Класс позволяет просматривать модель Category
    всем пользователям.

    Манипуляции с моделью Category разрешены
    исключительно администратору.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    search_fields = ('category__name')


class TitleViewSet(viewsets.ModelViewSet):
    """
    Класс позволяет просматривать модель Title
    всем пользователям.

    Манипуляции с моделью Title разрешены
    исключительно администратору.
    """

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_fields = (
        'category__slug', 'genre__slug', 'name', 'year'
    )
