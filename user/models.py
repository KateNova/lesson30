from django.contrib.auth.models import AbstractUser
from django.db import models

from ads.models import Location


class User(AbstractUser):

    MEMBER = 'member'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (MEMBER, 'Участник'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )

    locations = models.ManyToManyField(Location)
    role = models.CharField(choices=ROLE_CHOICES, default=MEMBER, max_length=20)
    age = models.IntegerField(default=0)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['username']
