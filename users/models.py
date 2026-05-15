import secrets

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import URLValidator
from django.db import models

from .managers import CustomUserManager
from .utils import validate_github_link, validate_phone_number

NAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField("Имя", max_length=NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(
        "Телефон",
        max_length=PHONE_MAX_LENGTH,
        validators=[validate_phone_number],
        blank=True,
        default="",
    )
    github_url = models.URLField(
        "GitHub", blank=True, default="", validators=[URLValidator(), validate_github_link]
    )
    about = models.TextField("О себе", max_length=ABOUT_MAX_LENGTH, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    saved_projects = models.ManyToManyField(
        "projects.Project", blank=True, related_name="interested_users"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
        ordering = ["-joined_at"]

    def get_full_name(self):
        return f"{self.name} {self.surname}"

    def __str__(self):
        return self.get_full_name()
