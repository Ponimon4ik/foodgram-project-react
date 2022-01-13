from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
        verbose_name='Еmail адрес',
        max_length=254, unique=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['username', 'email'],
                                    name='unique_user')
        ]
