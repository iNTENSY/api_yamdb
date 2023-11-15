
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    confirmation_code = models.UUIDField(
        verbose_name='Уникальный код',
        unique=True,
        null=True
    )
