from django.db import models

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