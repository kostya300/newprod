# users/views.py
from django_ratelimit.decorators import ratelimit
import requests
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# from psycopg.types.net import ip_address
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .forms import RegisterForm, LoginForm, ProfileEditForm, AvatarEditForm
from django.contrib.auth.views import LoginView
from django.views.generic import FormView
from django.contrib.auth import logout
import logging

from django.views import generic
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='ip', rate='3/m'), name='post')
@method_decorator(ratelimit(key='post:email', rate='5/m'), name='post')
class UserRegisterView(View):
    template_name = 'store/register.html'
    success_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Добро пожаловать, {user.username}! Вы успешно зарегистрировались."
            )
            next_page = request.GET.get('next')
            return redirect(next_page or 'home')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки ниже.")
        return render(request, self.template_name, {'form': form})


@method_decorator(ratelimit(key='ip', rate='5/m'), name='post') # 5 попыток с IP в минуту
@method_decorator(ratelimit(key='post:username', rate='3/m'), name='post')
class UserLoginView(View):
    template_name = 'store/login.html'  # Убедитесь, что путь правильный
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and self.redirect_authenticated_user:
            return redirect(self.success_url or 'home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {
            'form': form
        })

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"С возвращением, {user.username}!")
            next_page = request.GET.get('next')
            return redirect(next_page or 'home')
        else:
            return render(request, self.template_name, {
                'form': form
            })


def logout_view(request):
    logout(request)
    return redirect('home')

class ProfileView(LoginRequiredMixin, View):
    """
    Представление профиля пользователя.
    Показывает пользователя и определяет город по IP.
    Погода временно отключена.
    """
    template_name = 'store/profile.html'
    login_url = '/users/login/'
    def get(self, request):
        user = request.user
        # === Определяем город по IP ===
        try:
            ip_response = requests.get('http://ip-api.com/json/?fields=city', timeout=5)
            city_data = ip_response.json()
            city = city_data.get('city', 'Екатеринбург')
        except:
            city = 'Екатеринбург'

        context = {
            'user': user,
            'city': city,
            # 'weather' — временно убрано
        }
        return render(request, self.template_name, context)


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
