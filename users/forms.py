# users/forms.py
import os

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from .models import User

class RegisterForm(forms.Form):
    username = forms.CharField(
        label="Имя и фамилия",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'Введите email'})
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Введите номер'})
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Придумайте пароль'})
    )
    confirm_password = forms.CharField(
        label="Подтвердите пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            phone=self.cleaned_data["phone"]
        )
        user.bonus_points = 100  # бонус за регистрацию
        user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя'})
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_active:
            raise forms.ValidationError("Этот аккаунт отключен.", code='inactive')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Иван'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Иванов'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@domain.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 000-00-00'}),
        }

class AvatarEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'})
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if not avatar:
            raise forms.ValidationError("Пожалуйста, выберите файл изображения.")

        # Проверка типа файла — только для загружаемого файла (UploadedFile)
        if hasattr(avatar, 'content_type'):  # Проверяем, что это UploadedFile
            if not avatar.content_type.startswith('image/'):
                raise forms.ValidationError("Файл должен быть изображением.")

            # Проверка расширения по MIME‑типу
            valid_content_types = [
                'image/jpeg',
                'image/png',
                'image/gif',
                'image/webp'
            ]
            if avatar.content_type not in valid_content_types:
                raise forms.ValidationError(
                    "Допустимые форматы: JPG, PNG, GIF, WEBP."
                )

        # Проверка размера (максимум 2 МБ) — работает для обоих типов объектов
        if avatar.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Размер файла не должен превышать 2 МБ.")

        return avatar


