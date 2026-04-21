from store.models import Category
def categories_context(request):
    return {
        'categories':Category.objects.filter(is_active=True).order_by('name')
    }