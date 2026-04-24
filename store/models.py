from django.db import models

from users.models import User


class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание', blank=True,null=True)
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
    product = models.ForeignKey(Product,related_name='images',on_delete=models.CASCADE,verbose_name='Товар')
    image = models.ImageField("Изображение", upload_to="products/gallery/")
    order = models.PositiveIntegerField("Порядок",default=0)
    is_main = models.BooleanField("Основное изображение", default=False)
    class Meta:
        ordering = ['order']
        verbose_name = "Изображение товара"
        verbose_name_plural ="Галерея изображений"
    def __str__(self):
        return f"{self.product}- фото {self.order}"