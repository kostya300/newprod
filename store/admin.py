# store/admin.py
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, Product, Review, ProductImage, PriceComparison, Basket, Order, OrderItem


# === Вспомогательные функции ===
def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)


make_published.short_description = "Опубликовать выбранные отзывы"


def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_published=False)


make_unpublished.short_description = "Снять с публикации"


# === Inline: Отзывы внутри товара ===
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'created_at', 'rating')
    fields = ('user', 'rating', 'text', 'is_published', 'created_at')
    can_delete = True
    show_change_link = True


# === Inline: Товары в заказе ===
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'name', 'price', 'quantity', 'total_price')
    can_delete = False
    verbose_name = 'Товар'
    verbose_name_plural = 'Товары в заказе'


# === Inline: Изображения товара ===
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'order', 'is_main')
    ordering = ('order',)
    readonly_fields = ('is_main',)


# === Функция для отображения звёзд ===
def rating_stars(rating):
    full = '★' * int(rating)
    empty = '☆' * (5 - int(rating))
    return full + empty


# === Админка: Продукт ===
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def rating_display(self, obj):
        stars = rating_stars(obj.rating)
        return mark_safe(f'<span style="color: #ffc107;">{stars}</span> ({obj.rating})')

    rating_display.short_description = 'Рейтинг'

    list_display = (
        'name', 'category', 'price', 'old_price', 'in_stock',
        'is_featured', 'is_new', 'rating_display'
    )
    list_filter = ('category', 'in_stock', 'is_featured', 'is_new', 'created_at')
    list_editable = ('price', 'in_stock', 'is_featured', 'is_new')
    search_fields = ('name', 'description', 'slug')
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

    inlines = [ProductImageInline, ReviewInline]


# === Админка: Отзывы ===
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    def get_short_text(self, obj):
        return obj.text[:50] + '...' if obj.text and len(obj.text) > 50 else obj.text or '-'

    get_short_text.short_description = 'Текст отзыва'

    list_display = ('product', 'user', 'rating', 'get_short_text', 'is_published', 'created_at')
    list_filter = ('is_published', 'rating', 'created_at', 'product')
    list_editable = ('is_published',)
    search_fields = ('user__username', 'product__name', 'text')
    readonly_fields = ('created_at',)
    actions = [make_published, make_unpublished]


# === Админка: Категория ===
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fields = ('name', 'slug', 'description', 'image', 'is_active')


# === Админка: Сравнение цен ===
@admin.register(PriceComparison)
class PriceComparisonAdmin(admin.ModelAdmin):
    list_display = ('product', 'marketplace', 'price', 'created_at')
    list_filter = ('marketplace', 'created_at')
    search_fields = ('product__name',)


# === Админка: Корзина ===
@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_timestamp')
    list_filter = ('created_timestamp',)
    search_fields = ('user__username', 'product__name')


# === Админка: Заказ ===
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'first_name', 'last_name', 'total_amount',
        'status', 'delivery_type', 'payment_method', 'created_at'
    )
    list_filter = ('status', 'delivery_type', 'payment_method', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'phone', 'email')
    readonly_fields = ('created_at', 'total_amount')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Пользователь', {
            'fields': ('user', ('first_name', 'last_name'), 'phone', 'email')
        }),
        ('Доставка', {
            'fields': ('delivery_type', ('city', 'address', 'postal_code'))
        }),
        ('Оплата', {
            'fields': ('payment_method', 'total_amount', 'yookassa_payment_id')
        }),
        ('Статус', {
            'fields': ('status', 'created_at')
        }),
        ('Комментарий', {
            'fields': ('comment',)
        }),
    )


# === Админка: Товар в заказе ===
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'name', 'quantity', 'price', 'total_price')
    list_filter = ('order__status', 'product')
    search_fields = ('name', 'order__id', 'order__user__username')
    readonly_fields = ('total_price',)

    def has_add_permission(self, request):
        return False  # Создаётся автоматически при оформлении заказа

    def has_delete_permission(self, request, obj=None):
        return False  # Защита от случайного удаления