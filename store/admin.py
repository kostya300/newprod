# store/admin.py
from django.contrib import admin
from .models import Category, Product, ProductImage


# Inline для изображений товара
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # Количество пустых форм для загрузки новых фото
    fields = ('image', 'order', 'is_main')
    ordering = ('order',)
    readonly_fields = ('is_main',)  # Чтобы не редактировать вручную (см. совет ниже)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'description', 'image', 'is_active')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'old_price', 'in_stock', 'is_featured', 'is_new')
    list_filter = ('category', 'in_stock', 'is_featured', 'is_new', 'created_at')
    list_editable = ('price', 'in_stock', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description', 'category', 'price', 'old_price')
        }),
        ('Изображения и наличие', {
            'fields': ('image', 'in_stock', 'quantity')
        }),
        ('Маркетинг', {
            'fields': ('is_featured', 'is_new', 'rating', 'review_count')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Подключаем inline — чтобы добавлять фото прямо в форме товара
    inlines = [ProductImageInline]


# ⚠️ НЕ нужно регистрировать ProductImage отдельно!
# admin.site.register(ProductImage) — УДАЛИТЬ
# @admin.register(ProductImage) — УДАЛИТЬ