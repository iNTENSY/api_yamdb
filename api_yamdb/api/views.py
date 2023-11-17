import http
import uuid

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .serializers import (UserSerializer, SignUpSerializer,
                          TokenSerializer, CategorySerializer,
                          GenreSerializer, TitleSerializer,
                          ReviewSerializer, CommentSerializer)
from .permissions import IsAdmin, IsAdminOrReadOnly
from reviews.models import Category, Genre, Title, Review, Comment


User = get_user_model()


class SignUpAPIView(APIView):
    """
    Пользователь отправляет POST-запрос с параметрами
    email и username на эндпоинт. Сервис YaMDB отправляет
    письмо с кодом подтверждения (confirmation_code) на указанный адрес email.

    В конечном итоге должно формироваться и отправляться письмо.
    """

    def post(self, *args, **kwargs):
        serializer = SignUpSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')

        try:
            user, _ = User.objects.get_or_create(
                email=email,
                username=username
            )
        except IntegrityError:
            # Ошибка возникает, если хотя бы один из параметров
            # уже присутствует в базе данных у какого-то пользователя.
            # Ошибка возникает по причине присутствия параметра
            # unique у этих полей.
            raise ValidationError(detail='Invalid request data!')

        confirmation_code = self.make_token(user)

        send_mail(subject='Подтверждение аккаунта',
                  message=f'Код подтверждения: {confirmation_code}',
                  from_email='django@example.com',
                  recipient_list=[user.email])
        return Response({'email': f'{email}',
                         'username': f'{username}'},
                        status=http.HTTPStatus.OK)

    @staticmethod
    def make_token(user: User) -> uuid.UUID:
        """
        Метод генерирует код подтверждения, сохраняя
        его в поле confirmation_code для конкретного пользователя.
        Данный метод возвращает сгенерированный код для пользователя.
        """
        confirmation_code: uuid.UUID = uuid.uuid4()
        user.confirmation_code = confirmation_code
        user.save()
        return confirmation_code


class TokenAPIView(APIView):
    """
    Пользователь отправляет POST-запрос с
    параметрами username и confirmation_code на эндпоинт,
    в ответе на запрос ему приходит token (JWT-токен).
    """

    def post(self, *args, **kwargs):
        serializer = TokenSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'message': 'Invalid data!'},
                            status=http.HTTPStatus.NOT_FOUND)

        if user.confirmation_code == confirmation_code:
            token = AccessToken.for_user(user)
            return Response({'token': str(token)},
                            status=http.HTTPStatus.CREATED)
        return Response({'confirmation_code': 'Invalid token!'},
                        status=http.HTTPStatus.BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    Класс позволяет манипулировать моделью User
    исключительно администратором.

    Доступен путь ".../me/" для авторизованного
    пользователя (GET, PATCH запросы).
    """

    queryset = User.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(methods=['GET', 'PATCH'],
            detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
        return Response(serializer.data)


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


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
