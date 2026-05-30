# users/views.py
from django_ratelimit.decorators import ratelimit
import requests
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.shortcuts import render, redirect,get_object_or_404
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
from .models import EmailVerificationToken
from store.models import Order,Notification
from django.views import generic
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.urls import reverse
from .tasks import send_email_verification
logger = logging.getLogger(__name__)
def get_email_from_yandex(backend, details, response, user=None, *args, **kwargs):
    """
    Получает email из профиля Яндекса, если он не пришёл.
    """
    if backend.name == 'yandex-oauth2':
        if not details.get('email') and user:
            # Попробуем получить email из response
            emails = response.get('emails', [])
            if emails:
                details['email'] = emails[0]
    return {'details': details}

@method_decorator(ratelimit(key='ip', rate='3/m'), name='post')
@method_decorator(ratelimit(key='post:email', rate='5/m'), name='post')
class UserRegisterView(View):
    template_name = 'store/register.html'

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
            user = form.save(commit=False)
            user.is_verified = False
            user.save()
            print(f"✅ Пользователь сохранён: {user.email}")

            # Создаём токен
            token_obj, created = EmailVerificationToken.objects.get_or_create(user=user)
            print(f"✅ Токен: {token_obj.token}")

            # Получаем домен
            current_site = get_current_site(request)

            # Запускаем Celery-задачу в фоне
            send_email_verification.delay(user.id, current_site.domain)
            print("✅ Задача отправки email поставлена в очередь")

            messages.info(
                request,
                "Регистрация успешна! "
                "Пожалуйста, проверьте вашу почту — мы отправили письмо для подтверждения.",
                extra_tags="soft"
            )
            return render(request, 'info/verification_sent.html', {'user': user})
        else:
            print("❌ Форма невалидна:", form.errors)
            messages.error(request, "Пожалуйста, исправьте ошибки ниже.")
        return render(request, self.template_name, {'form': form})



@login_required
def notifications(request):
    # Показываем все уведомления пользователя
    notifications = request.user.notifications.all()
    # Отмечаем как прочитанные при заходе
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'store/notifications.html', {
        'notifications': notifications
    })
def verify_email(request, token):
    token_obj = get_object_or_404(EmailVerificationToken, token=token)
    user = token_obj.user
    if user.is_verified:
        messages.info(request,"Ваш аккаунт уже активирован")
    else:
        user.is_verified = True
        user.save()
        messages.success(request, "Email успешно подтверждён! Теперь можно войти.")
    # Удаляем токен после использования
    token_obj.delete()
    return redirect('users:login')
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

        order_count = Order.objects.filter(user=user).count()
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
            'order_count':order_count
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
