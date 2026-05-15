import secrets

from django.contrib.auth.models import BaseUserManager

from .utils import generate_avatar


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, name, surname, password, phone="", **extra):
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, phone=phone, **extra)
        user.set_password(password)

        if not user.avatar:
            avatar_content = generate_avatar(name[0] if name else "U")
            file_name = f"avatar_{secrets.token_hex(8)}.png"
            user.avatar.save(file_name, avatar_content, save=False)

        user.save(using=self._db)
        return user

    def create_user(self, email, name, surname, password=None, **extra):
        extra.setdefault("is_active", True)
        return self._create_user(email, name, surname, password, **extra)

    def create_superuser(self, email, name, surname, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(email, name, surname, password, **extra)
