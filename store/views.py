from django.shortcuts import render
def index(request):
    return render(request, 'store/index.html')
def catalog(request):
    return render(request, 'store/catalog.html')
def profile(request):
    return render(request, 'store/profile.html')
def login_view(request):
    return render(request, 'store/login.html')
def register_view(request):
    return render(request, 'store/register.html')
def products(request):
    return render(request, 'store/category/products.html')
def product_detail(request):
    return render(request,'store/category/cartoffthings.html')
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