from store.models import Category
from store.models import Basket
def categories_context(request):
    return {
        'categories': Category.objects.all()
    }
def cart_context(request):
    cart_total_items = 0
    if request.user.is_authenticated:
        cart_total_items = Basket.objects.filter(user=request.user).count()
    return {
        'cart_total_items': cart_total_items
    }