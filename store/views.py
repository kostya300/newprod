from django.shortcuts import render, get_object_or_404
from sympy.integrals.meijerint_doc import category

from .models import Category, Product


def index(request):
    featured_products = Product.objects.filter(is_featured=True,in_stock=True)[:9]
    categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/index.html', context)


def catalog(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/catalog.html', {
        'categories': categories,
    })
def products(request):
    category_slug = request.GET.get('category')
    category = None
    products = Product.objects.filter(in_stock=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    categories = Category.objects.filter(is_active=True)  # Для выпадающего меню

    return render(request, 'store/category/products.html', {
        'category': category,
        'products': products,
        'categories': categories,
    })



def profile(request):
    return render(request, 'store/profile.html')


def login_view(request):
    return render(request, 'store/login.html')


def register_view(request):
    return render(request, 'store/register.html')


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    gallery_images = product.images.all()
    main_image = product.image.url if product.image.url else None
    return render(request, 'store/category/cartoffthings.html',
                  {'product': product, 'gallery_images': gallery_images, 'main_image': main_image}
                  )


def my_favorites(request):
    # Здесь логика для страницы "Избранное"
    return render(request, 'store/category/myfavorite.html')


def cart(request):
    # Пример данных для корзины (в реальности — из сессии или БД)
    cart_items = [
        {
            'id': 1,
            'name': 'Phantom X2 Pro',
            'price': 59990,
            'quantity': 1,
            'image': 'https://via.placeholder.com/80/6a11cb/ffffff?text=Phone'
        },
        {
            'id': 2,
            'name': 'Quantum Buds',
            'price': 8990,
            'quantity': 2,
            'image': 'https://via.placeholder.com/80/00bfa5/ffffff?text=Buds'
        },
        {
            'id': 3,
            'name': 'Nebula Watch',
            'price': 19990,
            'quantity': 1,
            'image': 'https://via.placeholder.com/80/f57c00/ffffff?text=Watch'
        },
    ]
    return render(request, 'store/cart.html', {'cart_items': cart_items})


def contacts(request):
    return render(request, 'store/contacts.html')
