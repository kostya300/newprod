import re

import requests
from django.shortcuts import render, get_object_or_404, redirect
from flatbuffers.flexbuffers import Object
from sympy.integrals.meijerint_doc import category
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Category, Product,Basket
import base64
import time
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .utils import get_gigachat_token
from users.models import User
from .utils import get_gigachat_token  # ← из utils.py
from urllib.parse import quote  # ← для quote(user_query), если хотите
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

@csrf_exempt
@login_required
def basket_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Получаем количество из POST
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        quantity = 1

    # Пытаемся найти товар в корзине
    basket_item, created = Basket.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        # Если уже есть — увеличиваем
        basket_item.quantity += quantity
        basket_item.save()
    # Если новый — создан с нужным количеством

    # Возвращаемся на ту же страницу
    return redirect(request.META['HTTP_REFERER'])


GIGACHAT_TOKEN = "eyJjdHkiOiJqd3QiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.RLOoO2lvKCrRUFMRTK3AzOADyKM1xHmT0HPqQZ6LWmHIeey2KK8yPyLMNk2IYcr9wx4g1N1dWT-pKVNuBpJ0aRxNJr6F63Q5A21Wz06pwxnEv2F3O4_mjeNfN0ZDXjdX9rL1S8FHZAqD1_frIKyyB26p2BDDego6VADoNWdxIquoVZ1ncss9edkDl9AFxpVrEfcRuOdTp4pW9xUwW4f0vWI1UsASp8KRFJKIuBqqzgHGvnyzXWqJWvt0W9ANHtA_vZ2sTJe7kEKkfEeYW1Tjgp8C0y9freaTEI4UdsFFz_QH3am9ThAW4NMtfpleZW3IodMS4-TUP5SbdGPzEMMUYw.K6b-4aYjkY6zf7jmWtd__g.M-4SWEYdTdAglvDcH2xOCKvE5SRyCA7EBUu35bFpzh-VnArn2Rk5OKRqZeGeLEKiClRrgPAMK-bHbAKo1CmWu9nwRqmCGY--jRHfuzx9sv8ScIc8Kb7F1kpsba_LvfRM9R7088IaxBEcCYGqIZ00R1D0jTfvE0zS5gqjxr1FSy6v27HQNdZT1nLloFpxT_xoyanKi6TQ9TMrL7TCwvkrqw7SFdPsrDORHbiF66Z7kzeI1FJ0NnFAWnblZSNE3Ll8GBNhsuVqiFQntIgEAkawSvpz1juy6M9qkQnhnB8N-hMjPxs6GPpcSyuctbZOKiHN77Pisvi39twXanz25XR9FwNF3DzSPGanzJW9_w2obeA100OAnIjiLGlZbRx_oAZQcBSIygDnAMXMXEiM4ZdkbbLkaZuVMXAtONSrg_pC7869g0ew1De8N__bBeU9xm3RjGEv7MMNT25Rkpzu6M9aA8HxDmw0XOB4CY9dNzW7MMCO4VJCk1vheHhll_Oo3EWInkzMVlyYRM133cOXk0rlQKGjJjA9wsF_QuTnrtEbioLWHfzKaQMM3YAm3FwA-eIBbTfmBWM2-0-6RaKDpnO4KICYmCs0ZWPy2BkLeoYpqm0H_9BMYAtn_Uak7Qukc-hW6OHfgGagh-g-f4fvADiaAXtMCNTTyhPpdwSeISKd9fLcwb0EOkxUgy7QKkuhhjWMLpxle0yLpm5sIYEVBcN5ON8tylVWrXfU3HKN5OCmvQE.btIpUx-8BcdCigEi_N3wxlphzp-Dt2CtnMnnNSqHVjs"

# === Страница поиска товаров через ИИ ===

def goods_for_internet(request):
    products = []
    query = ""

    if request.method == "POST":
        query = request.POST.get("query", "").strip()

        if query:
            # Получаем токен
            token = get_gigachat_token()
            if not token:
                pass  # ошибка
            else:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }

                prompt = f"""
                Ты — помощник по поиску товаров. Верни JSON с 4-6 товарами: name, price, image, url, store.
                Пользователь ищет: "{query}"
                Если не знаешь — используй https://picsum.photos/300/200
                """

                payload = {
                    "model": "GigaChat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1024
                }

                response = requests.post(
                    "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    verify=False
                )

                if response.status_code == 200:
                    try:
                        content = response.json()['choices'][0]['message']['content']
                        start = content.find('[')
                        end = content.rfind(']') + 1
                        products = json.loads(content[start:end])

                        for p in products:
                            p['price'] = f"{p['price']:,}".replace(',', ' ')
                    except Exception as e:
                        print("Parse error:", e)

    return render(request, 'store/goodsforinternet.html', {
        'products': products,
        'query': query
    })

@csrf_exempt  # Разрешаем POST без CSRF (только если вызывается с JS)
def ai_internet_goods(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_query = data.get('query', '').strip()
            if not user_query:
                return JsonResponse({'products': []})

            # Попробуем получить токен
            token = get_gigachat_token()
            if not token:
                return JsonResponse({'error': 'Не удалось получить токен'}, status=500)

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            prompt = f"""
            Ты — помощник по поиску товаров в интернете.
            Пользователь ищет: "{user_query}"

            Верни ТОЛЬКО JSON-список из 4-6 товаров. Каждый товар должен содержать:
            - name (название)
            - price (цена в рублях, только число)
            - image (URL изображения с ОДНОГО из реальных сайтов: ozon.ru, wildberries.ru, beru.ru)
            - url (ссылка на товар)
            - store (название магазина)

            ❗ ВАЖНО:
            - Все ссылки должны начинаться с https://
            - Используй ТОЛЬКО настоящие, рабочие URL изображений
            - НЕ используй example.com, test.com, fakeimage.org
            - Если не знаешь точное изображение — используй https://picsum.photos/300/200

            Пример:
            [
              {{
                "name": "Наушники Sony WH-1000XM4",
                "price": 19990,
                "image": "https://cdn1.ozone.ru/s3/multimedia-1-w/6086526232.jpg",
                "url": "https://www.ozon.ru/product/naushniki-sony-wh-1000xm4-123456789/",
                "store": "Ozon"
              }}
            ]
            """

            payload = {
                "model": "GigaChat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1024
            }

            # Первая попытка
            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                headers=headers,
                json=payload,
                verify=False
            )

            # Если 401 — обновляем токен и пробуем ещё раз
            if response.status_code == 401:
                token = get_gigachat_token()  # принудительно обновляем
                if not token:
                    return JsonResponse({'error': 'Не удалось обновить токен'}, status=500)

                headers["Authorization"] = f"Bearer {token}"
                response = requests.post(
                    "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    verify=False
                )

            if response.status_code != 200:
                print("GigaChat API error:", response.status_code, response.text)
                return JsonResponse({'products': []})

            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            try:
                # Ищем массив JSON: [...]
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if not match:
                    print("JSON array not found")
                    products = []
                else:
                    json_str = match.group(0)
                    # Починим частые ошибки
                    json_str = json_str.replace('\n', '').strip()
                    # Добавим запятые, если забыты (простая эвристика)
                    json_str = re.sub(r'"}\s*"', '"},\n"', json_str)  # "key"}{" → "key"},{"
                    json_str = re.sub(r'}\s*{', '},{', json_str)

                    try:
                        products = json.loads(json_str)
                    except json.JSONDecodeError as je:
                        print("JSON parse error after fix:", je)
                        products = []

            except Exception as e:
                print("Unexpected error:", e)
                products = []
            # Извлекаем JSON
            try:
                start = content.find('[')
                end = content.rfind(']') + 1
                json_str = content[start:end]
                products = json.loads(json_str)
            except Exception as e:
                print("Parse error:", e)
                return JsonResponse({'products': []})

            # Форматируем цены
            for p in products:
                # Гарантированно рабочее изображение
                p['image'] = 'https://picsum.photos/seed/{}/300/200'.format(p.get('name', 'product'))

                # Форматируем цену
                try:
                    price = int(p['price'])
                    p['price'] = f"{price:,}".replace(',', ' ')
                except (ValueError, TypeError):
                    p['price'] = 'Цена не указана'

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({'products': []})

    return JsonResponse({'error': 'Only POST'}, status=400)
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
                verify=False
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
@login_required
def cart(request):
    # Только для текущего пользователя!
    cart_items = Basket.objects.filter(user=request.user).select_related('product')

    # Общая сумма — на сервере
    cart_total = sum(item.total_price for item in cart_items)

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })
@login_required
def basket_add_one(request, item_id):
    item = get_object_or_404(Basket, id=item_id, user=request.user)
    item.quantity += 1
    item.save()
    return redirect('cart')  # Возвращаемся в корзину

@login_required
def basket_remove_one(request, item_id):
    item = get_object_or_404(Basket, id=item_id, user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('cart')

@login_required
def basket_remove(request, item_id):
    item = get_object_or_404(Basket, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')

def contacts(request):
    return render(request, 'store/contacts.html')
