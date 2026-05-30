from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    phone = models.CharField("Телефон", max_length=15, blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)
    bonus_points = models.PositiveIntegerField("Бонусные баллы", default=0)
    discount = models.DecimalField("Скидка (%)", max_digits=3, decimal_places=1, default=0.0)
    is_verified = models.BooleanField('Email подтверждён', default=False)
    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
    def unread_notifications_count(self):
        return self.notifications.filter(is_read=False).count()

    def has_unread_notifications(self):
        return self.notifications.filter(is_read=False).exists()
    def __str__(self):
        return self.username
class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Верификация для {self.user.email}-{self.token}"