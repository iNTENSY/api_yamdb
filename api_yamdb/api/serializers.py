from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с пользователями.

    Отсутствуют поля сериализатора
    """

    class Meta:
        model = User
        fields = []


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с запросами по .../auth/signup/
    Принимает два поля username, email
    """
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Invalid username `me`!')
        return value


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, max_length=150)
    confirmation_code = serializers.UUIDField(required=True)

    class Meta:
        model = User
        fields = ['username', 'confirmation_code']
