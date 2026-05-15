import random
import re
import secrets
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

AVATAR_SIZE = 200
AVATAR_FONT_SIZE = 100
AVATAR_TEXT_COLOR = (255, 255, 255)
AVATAR_COLORS_LIST = [
    (70, 130, 200),
    (60, 140, 90),
    (210, 140, 80),
    (160, 100, 180),
    (80, 160, 160),
    (200, 100, 100),
]

PHONE_MAX_LENGTH = 12
GITHUB_PREFIXES = ("https://github.com", "http://github.com")


def generate_avatar(letter: str):
    color = random.choice(AVATAR_COLORS_LIST)
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=color)
    drawer = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()

    letter = letter.upper()
    bbox = drawer.textbbox((0, 0), letter, font=font)
    x = (AVATAR_SIZE - (bbox[2] - bbox[0])) // 2
    y = (AVATAR_SIZE - (bbox[3] - bbox[1])) // 2
    drawer.text((x, y), letter, fill=AVATAR_TEXT_COLOR, font=font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return ContentFile(buffer.read())


def validate_phone_number(value):
    if not (value.startswith("8") or value.startswith("+7")):
        raise ValidationError("Телефон должен начинаться с 8 или +7")
    if len(value) not in [11, 12]:
        raise ValidationError("Телефон должен содержать 11 цифр")
    if value.startswith("8") and not value[1:].isdigit():
        raise ValidationError("Некорректные символы в номере")
    if value.startswith("+7") and not value[2:].isdigit():
        raise ValidationError("Некорректные символы в номере")


def normalize_phone(phone: str) -> str:
    if phone.startswith("8") and len(phone) == 11:
        return "+7" + phone[1:]
    return phone


def validate_phone_format(phone: str) -> bool:
    pattern_8 = r"^8\d{10}$"
    pattern_7 = r"^\+7\d{10}$"
    return bool(re.match(pattern_8, phone) or re.match(pattern_7, phone))


def is_github_url(url: str) -> bool:
    return url.startswith(GITHUB_PREFIXES)


def validate_github_link(value):
    if value and "github.com" not in value:
        raise ValidationError("Ссылка должна вести на GitHub")
