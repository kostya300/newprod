from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    phone = models.CharField("Телефон", max_length=15, blank=True)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)
    bonus_points = models.PositiveIntegerField("Бонусные баллы", default=0)
    discount = models.DecimalField("Скидка (%)", max_digits=3, decimal_places=1, default=0.0)

    class Meta:
        db_table = "user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username