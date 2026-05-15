from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import User
from .utils import is_github_url, normalize_phone, validate_phone_format

NAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
PASSWORD_MIN_LENGTH = 8


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=NAME_MAX_LENGTH, label="Имя")
    surname = forms.CharField(max_length=NAME_MAX_LENGTH, label="Фамилия")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=PHONE_MAX_LENGTH, label="Телефон", required=False)
    password = forms.CharField(
        widget=forms.PasswordInput, label="Пароль", min_length=PASSWORD_MIN_LENGTH
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone:
            if not (phone.startswith("8") or phone.startswith("+7")):
                raise forms.ValidationError("Телефон должен начинаться с 8 или +7")
            if phone.startswith("8"):
                phone = "+7" + phone[1:]
            if User.objects.filter(phone=phone).exists():
                raise forms.ValidationError("Этот номер телефона уже используется")
        return phone

    def save(self):
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
            password=self.cleaned_data["password"],
            phone=self.cleaned_data.get("phone", ""),
        )


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url"]
        widgets = {"about": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)
        for field in ["avatar", "about", "phone", "github_url"]:
            self.fields[field].required = False

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return phone
        if not validate_phone_format(phone):
            raise forms.ValidationError("Введите номер в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")
        normalized = normalize_phone(phone)
        qs = User.objects.filter(phone=normalized)
        if self.current_user:
            qs = qs.exclude(pk=self.current_user.pk)
        if qs.exists():
            raise forms.ValidationError("Этот номер телефона уже используется.")
        return normalized

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "").strip()
        if not url:
            return url
        if not is_github_url(url):
            raise forms.ValidationError("Ссылка должна вести на GitHub (https://github.com/...).")
        return url


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput, min_length=8)
    new_password2 = forms.CharField(label="Подтверждение нового пароля", widget=forms.PasswordInput)
