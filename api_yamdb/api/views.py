import http
import uuid

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .serializers import (UserSerializer, GenreSerializer,
                          CategorySerializer, TitleSerializer, 
                          SignUpSerializer, TokenSerializer)
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
        serializer = SignUpSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')

        user, _ = User.objects.get_or_create(username=username, email=email)
        confirmation_code = uuid.uuid4()
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(subject='Подтверждение аккаунта',
                  message=f'Код подтверждения: {confirmation_code}',
                  from_email='django@example.com',
                  recipient_list=[user.email])
        return Response({'message': 'Email sent'}, status=http.HTTPStatus.OK)



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
        user = get_object_or_404(User, username=username)

        if user.confirmation_code == confirmation_code:
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=http.HTTPStatus.OK)
        return Response({'message': 'Invalid data!'}, status=http.HTTPStatus.BAD_REQUEST)


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
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            pass
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
    permission_classes = (permissions.IsAdminOrReadOnly,)
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
    permission_classes = (permissions.IsAdminOrReadOnly,)
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
    permission_classes = (permissions.IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_fields = (
        'category__slug', 'genre__slug', 'name', 'year'
    )
