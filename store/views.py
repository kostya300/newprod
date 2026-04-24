import requests
from django.shortcuts import render, get_object_or_404
from sympy.integrals.meijerint_doc import category
from django.http import JsonResponse
from .models import Category, Product
import base64
import time
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .utils import get_gigachat_token
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



GIGACHAT_TOKEN = "eyJjdHkiOiJqd3QiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.RLOoO2lvKCrRUFMRTK3AzOADyKM1xHmT0HPqQZ6LWmHIeey2KK8yPyLMNk2IYcr9wx4g1N1dWT-pKVNuBpJ0aRxNJr6F63Q5A21Wz06pwxnEv2F3O4_mjeNfN0ZDXjdX9rL1S8FHZAqD1_frIKyyB26p2BDDego6VADoNWdxIquoVZ1ncss9edkDl9AFxpVrEfcRuOdTp4pW9xUwW4f0vWI1UsASp8KRFJKIuBqqzgHGvnyzXWqJWvt0W9ANHtA_vZ2sTJe7kEKkfEeYW1Tjgp8C0y9freaTEI4UdsFFz_QH3am9ThAW4NMtfpleZW3IodMS4-TUP5SbdGPzEMMUYw.K6b-4aYjkY6zf7jmWtd__g.M-4SWEYdTdAglvDcH2xOCKvE5SRyCA7EBUu35bFpzh-VnArn2Rk5OKRqZeGeLEKiClRrgPAMK-bHbAKo1CmWu9nwRqmCGY--jRHfuzx9sv8ScIc8Kb7F1kpsba_LvfRM9R7088IaxBEcCYGqIZ00R1D0jTfvE0zS5gqjxr1FSy6v27HQNdZT1nLloFpxT_xoyanKi6TQ9TMrL7TCwvkrqw7SFdPsrDORHbiF66Z7kzeI1FJ0NnFAWnblZSNE3Ll8GBNhsuVqiFQntIgEAkawSvpz1juy6M9qkQnhnB8N-hMjPxs6GPpcSyuctbZOKiHN77Pisvi39twXanz25XR9FwNF3DzSPGanzJW9_w2obeA100OAnIjiLGlZbRx_oAZQcBSIygDnAMXMXEiM4ZdkbbLkaZuVMXAtONSrg_pC7869g0ew1De8N__bBeU9xm3RjGEv7MMNT25Rkpzu6M9aA8HxDmw0XOB4CY9dNzW7MMCO4VJCk1vheHhll_Oo3EWInkzMVlyYRM133cOXk0rlQKGjJjA9wsF_QuTnrtEbioLWHfzKaQMM3YAm3FwA-eIBbTfmBWM2-0-6RaKDpnO4KICYmCs0ZWPy2BkLeoYpqm0H_9BMYAtn_Uak7Qukc-hW6OHfgGagh-g-f4fvADiaAXtMCNTTyhPpdwSeISKd9fLcwb0EOkxUgy7QKkuhhjWMLpxle0yLpm5sIYEVBcN5ON8tylVWrXfU3HKN5OCmvQE.btIpUx-8BcdCigEi_N3wxlphzp-Dt2CtnMnnNSqHVjs"

@csrf_exempt
def ai_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            if not user_message:
                return JsonResponse({'response': 'Введите сообщение.'})

            # Получаем токен (с кэшированием!)
            token = get_gigachat_token()
            if not token:
                return JsonResponse({'response': 'Сервис временно недоступен. Ошибка авторизации.'})

            headers = {
                "Authorization": f"Bearer {token}",  # ✅ Не GIGACHAT_TOKEN, а token!
                "Content-Type": "application/json"
            }

            payload = {
                "model": "GigaChat",
                "messages": [
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7,
                "max_tokens": 512
            }

            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                headers=headers,
                json=payload,
                verify=False  # ⚠️ Только для разработки!
            )

            if response.status_code == 200:
                result = response.json()
                bot_reply = result['choices'][0]['message']['content'].strip()
                return JsonResponse({'response': bot_reply})
            else:
                print("GigaChat error:", response.status_code, response.text)
                return JsonResponse({'response': 'Не удалось получить ответ от AI.'})

        except Exception as e:
            print("Exception:", str(e))
            return JsonResponse({'response': 'Ошибка обработки запроса.'})

    return JsonResponse({'error': 'Only POST'}, status=400)





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

def radio(request):
    return render(request,'info/radio.html')
def currency(request):
    return render(request,'info/currency.html')
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
