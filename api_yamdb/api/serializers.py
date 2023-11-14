from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с пользователями.

    Отсутствуют поля сериализатора
    """

    class Meta:
        model = User
        fields = []
