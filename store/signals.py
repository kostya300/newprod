from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Product

@receiver(post_save, sender=Product)
def notify_admin_product_created_or_updated(sender, instance, created, **kwargs):
    """
    Отправляет email при добавлении/изменении товара.
    """
    if created:
        subject = f"🔔 Новинка: {instance.name}"
        message = (
            f"Товар: {instance.name}\n"
            f"Цена: {instance.price} ₽\n"
            f"https://myunitmyunit1.ru/admin/store/product/{instance.id}/change/"
        )
    else:
        subject = f"✏️ Товар изменён: {instance.name}"
        message = (
            f"Товар: {instance.name}\n"
            f"Цена: {instance.price} ₽\n"
            f"ID: {instance.id}\n"
        )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        print(f"✅ Email отправлен: {subject}")
    except Exception as e:
        print(f"❌ Email error: {e}")


@receiver(post_delete, sender=Product)
def notify_admin_product_deleted(sender, instance, **kwargs):
    """
    Отправляет email при удалении товара.
    """
    subject = f"🗑️ Товар удалён: {instance.name}"
    message = f"Товар {instance.name} (ID: {instance.id}) удалён из каталога."

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        print(f"✅ Email отправлен: {subject}")
    except Exception as e:
        print(f"❌ Email error: {e}")