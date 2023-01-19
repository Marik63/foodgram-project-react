from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Модель пользователей.
    """
    USER = 'user'
    ADMIN = 'admin'
    ROLES = [
        (ADMIN, 'ADMIN'),
        (USER, 'USER'),
    ]
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Username')
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        help_text='Введите электронную почту пользователя',
        max_length=254,
        unique=True)
    first_name = models.TextField(
        max_length=150,
        verbose_name='Имя',
        help_text='Введите имя пользователя')
    last_name = models.TextField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Введите фамилию пользователя')
    role = models.TextField(
        verbose_name='Роль',
        max_length=20,
        choices=ROLES,
        default=USER)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_user(self):
        return self.role == self.USER


class Meta:
    verbose_name = ' Пользователь'
    verbose_name_plural = 'Пользователи'
    ordering = ('username',)

    def __str__(self):
        return f'{self.username}'


class Follow(models.Model):
    """
    Модель подписок.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        related_name='following',
        verbose_name='Автор рецепта',
    )

    class Meta:
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]

    def __str__(self):
        return f'Пользователь: {self.user} подписан на {self.author}.'
