from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

from backend.constants import (
    EMAIL_VERBOSE_NAME, USERNAME_VERBOSE_NAME,
    EMAIL_ALREADY_REGISTERED,
    USERNAME_ALREADY_REGISTERED,
    USERNAME_HELP_TEXT, USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH,
    USERS_GET_SHORT_NAME
)


class User(AbstractUser):
    email = models.EmailField(
        verbose_name=EMAIL_VERBOSE_NAME,
        blank=False,
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
        error_messages={
            'unique': EMAIL_ALREADY_REGISTERED,
        },
    )
    username = models.CharField(
        verbose_name=USERNAME_VERBOSE_NAME,
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text=USERNAME_HELP_TEXT,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': USERNAME_ALREADY_REGISTERED,
        },
    )

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    def save(self, *args, **kwargs):
        if self.username == 'me':
            raise ValidationError('Username не может быть "me".')
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.is_superuser

    def get_short_name(self):
        return self.username[:USERS_GET_SHORT_NAME]

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username='me'),
                name='Пользователь не может быть назван me!'
            )
        ]


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_follow'
            )
        ]
