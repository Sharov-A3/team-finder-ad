import secrets
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.db import models
from django.core.validators import RegexValidator, URLValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
import random


AVATAR_COLORS_LIST = [
    (70, 130, 200),
    (60, 140, 90),
    (210, 140, 80),
    (160, 100, 180),
    (80, 160, 160),
    (200, 100, 100),
]

def validate_phone_number(value):
    if not (value.startswith('8') or value.startswith('+7')):
        raise ValidationError('Телефон должен начинаться с 8 или +7')
    if len(value) not in [11, 12]:
        raise ValidationError('Телефон должен содержать 11 цифр')
    if value.startswith('8') and not value[1:].isdigit():
        raise ValidationError('Некорректные символы в номере')
    if value.startswith('+7') and not value[2:].isdigit():
        raise ValidationError('Некорректные символы в номере')

def validate_github_link(value):
    """Проверка что ссылка ведёт на GitHub"""
    if value and 'github.com' not in value:
        raise ValidationError('Ссылка должна вести на GitHub')

class CustomUserManager(BaseUserManager):
  

    def _create_user(self, email, name, surname, password, phone='', **extra):
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, phone=phone, **extra)
        user.set_password(password)
        

        if not user.avatar:
            avatar_content = self._make_avatar(name[0] if name else 'U')
            file_name = f"avatar_{secrets.token_hex(8)}.png"
            user.avatar.save(file_name, avatar_content, save=False)
        
        user.save(using=self._db)
        return user
    
    def create_user(self, email, name, surname, password=None, **extra):
        extra.setdefault('is_active', True)
        return self._create_user(email, name, surname, password, **extra)
    
    def create_superuser(self, email, name, surname, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self._create_user(email, name, surname, password, **extra)
    
    @staticmethod
    def _make_avatar(letter):

        color = random.choice(AVATAR_COLORS_LIST)
        image = Image.new('RGB', (200, 200), color=color)
        drawer = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except:
            font = ImageFont.load_default()
        
        letter = letter.upper()
        bbox = drawer.textbbox((0, 0), letter, font=font)
        x = (200 - (bbox[2] - bbox[0])) // 2
        y = (200 - (bbox[3] - bbox[1])) // 2
        drawer.text((x, y), letter, fill=(255, 255, 255), font=font)
        
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return ContentFile(buffer.read())

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField('Имя', max_length=124)
    surname = models.CharField('Фамилия', max_length=124)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone = models.CharField(
        'Телефон',
        max_length=12,
        validators=[validate_phone_number],
        blank=True,
        default=''
    )
    github_url = models.URLField(
        'GitHub',
        blank=True,
        default='',
        validators=[URLValidator(), validate_github_link]
    )
    about = models.TextField('О себе', max_length=256, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    

    saved_projects = models.ManyToManyField(
    'projects.Project',
    blank=True,
    related_name='interested_users'  
)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']
    
    objects = CustomUserManager()
    
    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        ordering = ['-joined_at']
    
    def get_full_name(self):
        return f'{self.name} {self.surname}'
    
    def __str__(self):
        return self.get_full_name()