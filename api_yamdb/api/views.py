import http
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .serializers import UserSerializer, SignUpSerializer, TokenSerializer
from .permissions import IsAdmin


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
            user, is_created = User.objects.get_or_create(
                email=email,
                username=username)
        except IntegrityError:
            raise ValidationError(detail='Invalid request data!')

        confirmation_code = default_token_generator.make_token(user)
        send_mail(subject='Подтверждение аккаунта',
                  message=f'Код подтверждения: {confirmation_code}',
                  from_email='django@example.com',
                  recipient_list=[user.email])
        return Response({'email': f'{email}', 'username': f'{username}'}, status=http.HTTPStatus.OK)



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
            return Response({'message': 'not now'}, status=http.HTTPStatus.NOT_FOUND)

        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=http.HTTPStatus.CREATED)
        return Response({'confirmation_code': ['Invalid token!']}, status=http.HTTPStatus.BAD_REQUEST)


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