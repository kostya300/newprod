from django.shortcuts import render, get_object_or_404
from sympy.integrals.meijerint_doc import category
from django.http import JsonResponse
from .models import Category, Product


def index(request):
    featured_products = Product.objects.filter(is_featured=True,in_stock=True)[:9]
    categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'store/index.html', context)

# filter page for desktop
def filter_page(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    # Обработка фильтров
    q = request.GET.get('q')
    category_slug = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if q:
        products = products.filter(name__icontains=q)
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        'products': products,
        'categories': categories,
        'current_query': q or '',  # ← ВАЖНО: если None → превратить в пустую строку
        'current_category': category_slug or '',
        'current_min_price': min_price or '',
        'current_max_price': max_price or '',
    }
    return render(request, 'store/catalog/filter.html', context)

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
