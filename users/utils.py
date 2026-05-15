import re

PHONE_PATTERN_8 = r"^8\d{10}$"
PHONE_PATTERN_7 = r"^\+7\d{10}$"

def validate_phone_format(phone: str) -> bool:
    return bool(re.match(PHONE_PATTERN_8, phone) or re.match(PHONE_PATTERN_7, phone))

def normalize_phone(phone: str) -> str:
    if phone.startswith("8") and len(phone) == 11:
        return "+7" + phone[1:]
    return phone

def is_github_url(url: str) -> bool:
    return url.startswith("https://github.com") or url.startswith("http://github.com")