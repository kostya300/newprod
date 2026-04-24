# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'bonus_points', 'discount')
    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительно", {
            "fields": ("phone", "avatar", "bonus_points", "discount")
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Дополнительно", {
            "fields": ("phone", "avatar", "bonus_points", "discount")
        }),
    )