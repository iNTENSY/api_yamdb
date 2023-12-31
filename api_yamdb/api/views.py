import http

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters, mixins
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb import settings
from .filters import TitlesFilter
from .serializers import (UserSerializer, SignUpSerializer,
                          TokenSerializer, CategorySerializer,
                          GenreSerializer, TitleSerializer,
                          ReviewSerializer, CommentSerializer,
                          ReadOnlyTitleSerializer)
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrModeratorOrAdminOrReadOnly)
from reviews.models import Category, Genre, Title, Review
from django.shortcuts import get_object_or_404


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
        user = User.objects.get(username=username)

        confirmation_code = default_token_generator.make_token(user)

        send_mail(subject='Подтверждение аккаунта',
                  message=f'Код подтверждения: {confirmation_code}',
                  from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=[user.email])
        return Response({'email': f'{email}',
                         'username': f'{username}'},
                        status=http.HTTPStatus.OK)


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
        user = User.objects.get(username=username)

        if default_token_generator.check_token(user, confirmation_code):
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


class GenreViewSet(viewsets.GenericViewSet,
                   mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin):
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
    pagination_class = LimitOffsetPagination
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(viewsets.GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin):
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
    pagination_class = LimitOffsetPagination
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Класс позволяет просматривать модель Title
    всем пользователям.
    Манипуляции с моделью Title разрешены
    исключительно администратору.
    """

    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'head', 'delete', 'patch']

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Действия с отзывами"""
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthorOrModeratorOrAdminOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    ]
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'delete',
                         'head', 'options', 'patch', 'trace']

    def get_queryset(self):
        return get_object_or_404(
            Title, pk=self.kwargs.get('title_id')
        ).reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(
            author=self.request.user, title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Действия с комментариями"""
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'delete', 'head',
                         'options', 'patch', 'trace']
    permission_classes = [
        IsAuthorOrModeratorOrAdminOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    ]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(
            Review, pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        serializer.save(
            author=self.request.user, review=review
        )
