from django.db import models

class Category(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение категории', upload_to='static/categories/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('Название', max_length=200)
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
