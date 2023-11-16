from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


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

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Invalid username: `me`!')
        return value


class TokenSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'confirmation_code']
