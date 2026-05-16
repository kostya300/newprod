# store/admin.py
from django.contrib import admin
from .models import Category, Product, ProductImage,Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Не показывать пустые строки
    readonly_fields = ('product', 'name', 'price', 'quantity', 'total_price')
    can_delete = False
    verbose_name = 'Товар'
    verbose_name_plural = 'Товары в заказе'
# Админка для заказа
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'first_name',
        'last_name',
        'total_amount',
        'status',
        'delivery_type',
        'payment_method',
        'created_at',
    )
    list_filter = (
        'status',
        'delivery_type',
        'payment_method',
        'created_at',
    )
    search_fields = (
        'id',
        'user__username',
        'user__email',
        'first_name',
        'last_name',
        'phone',
        'email',
    )
    readonly_fields = (
        'created_at',
        'total_amount',
    )
    inlines = [OrderItemInline]
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
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
# Админка для OrderItem (опционально — если хочется отдельно)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'name', 'quantity', 'price', 'total_price')
    list_filter = ('order__status', 'product')
    search_fields = ('name', 'order__id', 'order__user__username')
    readonly_fields = ('total_price',)

    def has_add_permission(self, request):
        return False  # Создаётся через Order
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