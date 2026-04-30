# users/views.py

import requests
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from psycopg.types.net import ip_address

from .forms import RegisterForm, LoginForm, ProfileEditForm, AvatarEditForm
from django.contrib.auth.views import LoginView
from django.views.generic import FormView
from django.contrib.auth import logout
import logging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='ip', rate='3/m'), name='post')  # макс. 3 попытки в минуту с IP
@method_decorator(ratelimit(key='post:email', rate='5/h'), name='post')  # 5 регистраций на email в час
class UserRegisterView(FormView):
    template_name = 'store/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        # Если пользователь уже залогинен — не показываем регистрацию
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request,
            f"Добро пожаловать, {user.username}! Вы успешно зарегистрировались."
        )
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки ниже.")
        return super().form_invalid(form)

    def get_success_url(self):
        # Поддержка ?next= после регистрации
        next_page = self.request.GET.get('next')
        return next_page or self.success_url


class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = 'store/login.html'
    redirect_authenticated_user = True  # если залогинен — не показывать форму
    success_url = reverse_lazy('home')

    def get_success_url(self):
        # Поддержка ?next=...
        next_page = self.request.GET.get('next')
        if next_page:
            return next_page
        return super().get_success_url()

    def form_invalid(self, form):
        # Можно добавить кастомные сообщения
        from django.contrib import messages
        messages.error(self.request, "Неверные данные для входа или учётная запись отключена.")
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    return redirect('home')



@login_required
def profile(request):
    user = request.user

    # === 1. Определяем город по IP ===
    try:
        ip_response = requests.get('http://ip-api.com/json/?fields=city', timeout=5)
        city_data = ip_response.json()
        city = city_data.get('city', 'Екатеринбург')  # ← Используем кириллицу!
    except:
        city = 'Екатеринбург'

    # === 2. Погода через Яндекс ===
    weather = {
        'icon': '🌤',
        'temp': '—°C',
        'location': 'Ошибка'
    }

    try:
        api_key = 'ВАШ_КЛЮЧ_ЯНДЕКС'  # ← ЗАМЕНИТЬ!
        url = f'https://api.weather.yandex.ru/v2/forecast?city={city}&lang=ru_RU'

        headers = {
            'X-Yandex-API-Key': api_key
        }

        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        if 'fact' in data:
            fact = data['fact']
            temp = fact['temp']
            condition = fact['condition']

            # Эмодзи по погоде
            icons = {
                'clear': '☀️',
                'partly-cloudy': '⛅',
                'cloudy': '☁️',
                'overcast': '☁️',
                'light-rain': '🌦',
                'rain': '🌧',
                'heavy-rain': '⛈',
                'downpour': '🌧',
                'hail': '🌨',
                'thunderstorm': '⛈',
                'thunderstorm-with-rain': '⛈',
                'snow': '❄️',
                'light-snow': '🌨',
                'wet-snow': '🌨',
                'snow-showers': '🌨',
                'fog': '🌫',
                'dust': '💨',
                'haze': '🌫',
                'light-snow-showers': '🌨',
                'moderate-snow-showers': '🌨',
                'heavy-snow-showers': '🌨',
            }

            weather = {
                'icon': icons.get(condition, '🌤'),
                'temp': f'{temp}°C',
                'location': city
            }
    except Exception as e:
        print("Ошибка погоды (Яндекс):", e)

    context = {
        'user': user,
        'weather': weather,
    }
    return render(request, 'store/profile.html', context)


@login_required
def settings_view(request):
    user = request.user
    form = ProfileEditForm(instance=user)
    avatar_form = AvatarEditForm(instance=user)

    if request.method == 'POST':
        if 'save_profile' in request.POST:
            form = ProfileEditForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "Данные успешно обновлены.")
                return redirect('users:settings')
            else:
                messages.error(request, "Ошибка в данных профиля.")

        elif 'upload_avatar' in request.POST:
            avatar_form = AvatarEditForm(request.POST, request.FILES, instance=user)
            logger.info(f"Received files: {request.FILES}")
            logger.info(f"Form data: {request.POST}")

            if avatar_form.is_valid():
                # Сохраняем форму — это должно сохранить файл
                avatar_form.save()

                # Дополнительная проверка: действительно ли файл сохранён
                if user.avatar and user.avatar.name:
                    logger.info(f"Avatar saved successfully: {user.avatar.path}")
                    messages.success(request, "Аватар успешно обновлён.")
                else:
                    logger.error("Avatar was not saved to the database")
                    messages.error(request, "Ошибка сохранения аватара.")
            else:
                logger.error(f"Avatar form errors: {avatar_form.errors}")
                messages.error(request, f"Ошибка загрузки аватара: {avatar_form.errors}")

    return render(request, 'store/settings.html', {
        'form': form,
        'avatar_form': avatar_form,
        'user': user
    })
