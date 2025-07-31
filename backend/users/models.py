from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='User Name',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Use Valid symbols for username.'
            )
        ]
    )
    first_name = models.CharField(
        max_length=256, verbose_name='First Name'
    )
    last_name = models.CharField(
        max_length=256, verbose_name='Last Name'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name=' User'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Author')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user.username} follows {self.author.username}'
