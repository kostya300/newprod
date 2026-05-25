from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from users.models import User
from django.contrib.auth import get_user_model


class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание', blank=True, null=True)
    image = models.ImageField('Изображение категории', upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    old_price = models.DecimalField('Старая цена', max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    image = models.ImageField('Основное изображение', upload_to='products/')
    is_featured = models.BooleanField('Рекомендуемый', default=False)  # Для главной страницы
    is_new = models.BooleanField('Новинка', default=True)
    in_stock = models.BooleanField('В наличии', default=True)
    quantity = models.PositiveIntegerField('Количество на складе', default=0)
    rating = models.FloatField('Рейтинг', default=0.0)
    review_count = models.PositiveIntegerField('Число отзывов', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/product/{self.slug}/"

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((1 - self.price / self.old_price) * 100)
        return 0


# store/models.py

class Comment(MPTTModel):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField('Текст', max_length=3000)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    class MPTTMeta:
        order_insertion_by = ['-created_at']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.text[:50]}'


# store/models.py
class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительский отзыв'
    )
    rating = models.PositiveIntegerField(
        'Оценка',
        choices=[(i, str(i)) for i in range(1, 6)],
        null=True,
        blank=True
    )
    text = models.TextField('Отзыв', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField('Опубликован', default=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.text[:50]}"

    @property
    def likes_count(self):
        return self.likes.count()


class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return f"{self.user} → {self.review}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Нельзя добавить дважды
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class PriceComparison(models.Model):
    MARKETPLACES = (
        ('books_to_scrape', 'BooksToScrape'),
        ('google_books', 'Google Книги'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_competitors')
    marketplace = models.CharField(max_length=20, choices=MARKETPLACES)
    price = models.PositiveIntegerField(verbose_name="Цена")
    url = models.URLField(verbose_name="Ссылка")

    title = models.CharField(max_length=200, blank=True, verbose_name="Название книги")
    image = models.URLField(blank=True, verbose_name="Обложка")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'marketplace')
        verbose_name = "Цена у конкурента"
        verbose_name_plural = "Цены у конкурентов"

    def __str__(self):
        return f"{self.get_marketplace_display()} — {self.price} ₽"


User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('pending', 'Ожидает оплаты'),
        ('succeeded', 'Оплачен'),
        ('cancelled', 'Отменён'),
    ]

    DELIVERY_CHOICES = [
        ('pickup', 'Самовывоз'),
        ('courier', 'Доставка курьером'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Наличными при получении'),
        ('card', 'Онлайн-оплата картой'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    comment = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    yookassa_payment_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='created')  # created, pending, succeeded, cancelled
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ {self.id} — {self.get_status_display()}"

    def get_payment_url(self):
        if self.yookassa_payment_id and self.status != 'succeeded':
            return f"https://yookassa.ru/my/payments/{self.yookassa_payment_id}"
        return None


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    name = models.CharField('Название', max_length=255)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)
    total_price = models.DecimalField('Общая стоимость', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f"{self.quantity} × {self.name} в заказе {self.order.id}"

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)


class Basket(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    product = models.ForeignKey(  # ← не products, а product
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(default=1)  # Лучше default=1, а не 0
    created_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Корзина'
        ordering = ['created_timestamp']
        unique_together = ('user', 'product')  # Запрещает дубли

    def __str__(self):
        return f'Корзина: {self.user.email} | {self.product.name} × {self.quantity}'

    @property
    def total_price(self):
        """Общая стоимость позиции"""
        return self.quantity * self.product.price

    @property
    def name(self):
        return self.product.name

    @property
    def price(self):
        return self.product.price

    @property
    def image(self):
        """Возвращает основное или первое изображение товара"""
        main_img = self.product.images.filter(is_main=True).first()
        if main_img:
            return main_img.image.url
        first_img = self.product.images.first()
        if first_img:
            return first_img.image.url
        return '/static/images/no-image.png'  # заглушка


# модель ProductImage для хранения дополнительных изображений.
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name='Товар')
    image = models.ImageField("Изображение", upload_to="products/gallery/")
    order = models.PositiveIntegerField("Порядок", default=0)
    is_main = models.BooleanField("Основное изображение", default=False)

    class Meta:
        ordering = ['order']
        verbose_name = "Изображение товара"
        verbose_name_plural = "Галерея изображений"

    def __str__(self):
        return f"{self.product}- фото {self.order}"
