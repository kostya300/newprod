# users/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .models import EmailVerificationToken


@shared_task
def send_email_verification(user_id, domain):
    """
        Отправляет письмо с подтверждением email.
        Запускается как фоновая задача через Celery.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        token_obj, created = EmailVerificationToken.objects.get_or_create(user=user)
        token = token_obj.token
        # Генерируем ссылку
        verification_link = reverse('users:verify_email', args=[token])
        full_link = f"http://{domain}{verification_link}"
        # Подготавливаем HTML-письмо
        html_message = render_to_string('info/verification.html', {
            'user': user,
            'verification_link': full_link,
        })
        plain_message = strip_tags(html_message)
        send_mail(
        subject='Подтвердите ваш email',
        message=plain_message,
        from_email='noreply@вашсайт.рф',
        recipient_list=[user.email],
        fail_silently=False,
        html_message=html_message,
        )
        print(f"✅ Письмо подтверждения отправлено на {user.email}")
        return f"Email sent to {user.email}"
    except Exception as e:
        print(f"❌ Ошибка при отправке email: {e}")
        return f"Error: {str(e)}"
