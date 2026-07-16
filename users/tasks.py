# users/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .models import EmailVerificationToken  # ← ВАЖНО: добавлено
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_email_verification(user_id, domain):
    """
    Отправляет письмо с подтверждением email.
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        token_obj, created = EmailVerificationToken.objects.get_or_create(user=user)
        token = token_obj.token

        verification_link = reverse('users:verify_email', args=[token])
        full_link = f"https://{domain}{verification_link}"

        html_message = render_to_string('info/verification.html', {
            'user': user,
            'verification_link': full_link,
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject='Подтвердите ваш email — ВИКИ',
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message,
        )

        logger.info(f"✅ Письмо подтверждения отправлено на {user.email}")
        return f"Email sent to {user.email}"
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке email: {e}")
        return f"Error: {str(e)}"