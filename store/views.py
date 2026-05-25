import re
from django.db.models import Avg
from django.utils.formats import date_format
from django.utils.timezone import localtime
from django.views import View
from django.views.decorators.http import require_http_methods

from newprod import settings
import requests
from rest_framework.response import Response
from .forms import CommentCreateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from django.contrib.admin.templatetags.admin_list import pagination
from django.core.paginator import Page, Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from flatbuffers.flexbuffers import Object
from rest_framework.decorators import api_view
from sympy.integrals.meijerint_doc import category
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from yookassa import Configuration, Configuration, Payment
import uuid
from .models import Category, Product, Basket, Order, OrderItem, Review, Favorite, ReviewLike, Comment
import base64
import time
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .serializers import CartItemSerializer
from .utils import get_gigachat_token
from users.models import User
from .utils import get_gigachat_token  # ← из utils.py
from urllib.parse import quote  # ← для quote(user_query), если хотите
import logging
from django.core.cache import cache
logger = logging.getLogger(__name__)


def get_deal_of_day():
    deal = cache.get('deal_of_day')
    if not deal:
        deal = Product.objects.filter(is_featured=True).order_by('?').first()
        cache.set('deal_of_day', deal, 60 * 60 * 24)  # 24 часа
    return deal
class IndexView(ListView):
    template_name = 'store/index.html'
    context_object_name = 'featured_products'

    def get_queryset(self):
        """
        Мы НЕ используем этот queryset напрямую,
        но он нужен для совместимости с ListView.
        Реальную логику делаем в get_context_data.
        """
        return Product.objects.none()  # заглушка

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем page из GET
        page = self.request.GET.get('page', 1)
        try:
            page = int(page)
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1

        # Фильтруем и ОБРЕЗАЕМ до 6 товаров (как в FBV)
        featured_products_list = Product.objects.filter(
            is_featured=True,
            in_stock=True
        )[:6]


        # Пагинация: по 3 на страницу
        paginator = Paginator(featured_products_list, 3)

        try:
            featured_products = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            featured_products = paginator.page(1)

        # Добавляем в контекст
        context['featured_products'] = featured_products
        context['deal_product'] = get_deal_of_day()
        context['categories'] = Category.objects.filter(is_active=True)[:6]

        return context


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


class CatalogView(ListView):
    template_name = 'store/catalog.html'
    context_object_name = 'featured_products'  # чтобы в шаблоне осталось featured_products

    def get_queryset(self):
        # Заглушка — не используется, но нужна для ListView
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Все активные категории
        categories = Category.objects.filter(is_active=True)

        # Получаем номер страницы
        page = self.request.GET.get('page', 1)

        # Фильтруем ВСЕ избранные товары (без [:6])
        featured_products_list = Product.objects.filter(
            is_featured=True,
            in_stock=True
        )

        # Пагинация: 3 товара на страницу
        per_page = 3
        paginator = Paginator(featured_products_list, per_page)

        try:
            featured_products = paginator.page(page)
        except PageNotAnInteger:
            featured_products = paginator.page(1)
        except EmptyPage:
            featured_products = paginator.page(paginator.num_pages)
        except Exception:
            featured_products = paginator.page(1)

        # Добавляем в контекст
        context['featured_products'] = featured_products
        context['categories'] = categories

        return context


class ProductsListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'store/category/products.html'
    paginate_by = 2
    paginate_orphans = 1

    def get_queryset(self):
        """Фильтруем товары по категории и доступности"""
        queryset = Product.objects.filter(in_stock=True)
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Текущая категория
        category_slug = self.request.GET.get('category')
        context['category'] = None
        if category_slug:
            context['category'] = get_object_or_404(Category, slug=category_slug)
        # Все активные категории (для фильтра)
        context['categories'] = Category.objects.filter(is_active=True)
        context['featured_products'] = Product.objects.filter(
            is_featured=False,
            in_stock=True
        )[:6]
        context['current_category'] = category_slug or ''
        return context
def product_search(request):
    """
    Поиск товаров по названию
    """
    query = request.GET.get('q', '').strip()
    products = []

    if query:
        # Ищем по названию (регистронезависимо)
        products = Product.objects.filter(
            name__icontains=query
        ).filter(
            in_stock=True
        )[:10]  # Ограничиваем выборку

    return render(request, 'store/search_results.html', {
        'products': products,
        'query': query
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


def order_success(request, order_id):
    """Страница подтверждения заказа"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        if order.payment_method == 'card':
            message = "Ожидайте письмо с подтверждением оплаты."
        else:  # cash
            message = "Заказ оформлен! Оплата наличными при получении."
    except Order.DoesNotExist:
        order = None
        message = "Заказ не найден или доступ запрещён."

    return render(request, 'store/order_success.html', {
        'order_id': order_id,
        'message': message
    })


# @csrf_exempt
# @login_required
# def basket_add(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#
#     # Получаем количество из POST
#     quantity = int(request.POST.get('quantity', 1))
#     if quantity < 1:
#         quantity = 1
#
#     # Пытаемся найти товар в корзине
#     basket_item, created = Basket.objects.get_or_create(
#         user=request.user,
#         product=product,
#         defaults={'quantity': quantity}
#     )
#
#     if not created:
#         # Если уже есть — увеличиваем
#         basket_item.quantity += quantity
#         basket_item.save()
#     # Если новый — создан с нужным количеством
#
#     # Возвращаемся на ту же страницу
#     return redirect(request.META['HTTP_REFERER'])


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

@login_required
@require_http_methods(["POST"])
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    comment.delete()
    return JsonResponse({'status': 'ok'})


# store/views.py
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime
class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = CommentCreateForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            product = get_object_or_404(Product, id=kwargs.get('product_id'))
            comment.product = product
            comment.user = request.user


            parent_id = form.cleaned_data.get('parent')
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id, product=product)
                    comment.parent = parent_comment  # Это ForeignKey — присваиваем объект
                except Comment.DoesNotExist:
                    pass

            comment.save()
            avatar_url = comment.user.avatar.url if comment.user.avatar else '/static/images/default-avatar.png'
            user_slug = comment.user.username.lower()

            return JsonResponse({
                'id': comment.id,
                'user': comment.user.username,
                'user_slug': user_slug,
                'text': comment.text,
                'created_at': comment.created_at.strftime('%d %b %Y %H:%M'),
                'is_child': bool(comment.parent_id),
                'parent_id': comment.parent_id,
                'avatar': avatar_url,
                'is_my': True,
            })

        return JsonResponse({'error': form.errors}, status=400)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    gallery_images = product.images.all()
    main_image = product.image.url if product.image else '/static/images/no-image.png'

    # Все комментарии, включая вложенные
    comments = product.comments.all().order_by('tree_id', 'lft')
    print(f"🔍 Найдено комментариев: {comments.count()}")

    user_rating = None
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()
        if user_review:
            user_rating = user_review.rating

    return render(request, 'store/category/cartoffthings.html', {
        'product': product,
        'gallery_images': gallery_images,
        'main_image': main_image,
        'comments': comments,
        'user_rating': user_rating,
        'form': CommentCreateForm(),
    })

@csrf_exempt
@login_required
def like_review(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            review_id = data.get('review_id')
            review = get_object_or_404(Review, id=review_id)
            like, created = ReviewLike.objects.get_or_create(review=review, user=request.user)
            if not created:
                like.delete()
                liked = False
            else:
                liked = True
            return JsonResponse({
                'status': 'ok',
                'liked': liked,
                'likes_count': review.likes.count()
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@csrf_exempt
@login_required
def save_rating(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            rating = data.get('rating')

            if not product_id or not rating or rating < 1 or rating > 5:
                return JsonResponse({'error': 'Некорректные данные'}, status=400)

            product = get_object_or_404(Product, id=product_id)

            # Создаём или обновляем отзыв
            review, created = Review.objects.update_or_create(
                user=request.user,
                product=product,
                defaults={
                    'rating': rating,
                    'is_published': True,
                }
            )

            # Пересчитываем средний рейтинг
            reviews = product.reviews.filter(is_published=True)
            avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            product.rating = round(avg_rating, 1)
            product.review_count = reviews.count()
            product.save()

            return JsonResponse({
                'status': 'ok',
                'rating': product.rating,
                'review_count': product.review_count
            })

        except Exception as e:
            # Логируем ошибку
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка при сохранении рейтинга: {str(e)}")
            return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)


@login_required
def order_history(request):
    """Отображает историю заказов пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/history_orders.html', {'orders': orders})


def order_view(request):
    print("🔹 Пользователь:", request.user)
    print("🔹 Аутентифицирован:", request.user.is_authenticated)
    """Отображает страницу оформления заказа"""
    return render(request, 'store/includes/ordersection.html')


@login_required
def about_order(request, order_id):
    """Страница деталей заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Получаем реальные товары из OrderItem
    order_items = []
    for item in order.items.all():  # related_name='items'
        order_items.append({
            'name': item.name,
            'price': item.price,
            'quantity': item.quantity,
            'total_price': item.total_price,
            'image': item.product.image.url if item.product.image else '/static/images/no-image.png'
        })
    return render(request, 'store/about_order.html', {
        'order': order,
        'order_items': order_items
    })


# Настройка YooKassa
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """API: создаёт заказ и платёж в YooKassa"""
    user = request.user
    data = request.data

    # Проверка авторизации
    if not user.is_authenticated:
        return Response({"error": "Требуется вход"}, status=401)

    # Сумма из корзины
    cart_items = Basket.objects.filter(user=user).select_related('product')
    total_amount = sum(item.total_price for item in cart_items)
    if total_amount <= 0:
        return Response({"error": "Корзина пуста"}, status=400)

    # Создаём заказ
    order = Order.objects.create(
        user=user,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone=data.get('phone'),
        email=data.get('email'),
        delivery_type=data.get('delivery_type'),
        city=data.get('city'),
        address=data.get('address'),
        postal_code=data.get('postal_code'),
        payment_method=data.get('payment_method'),
        comment=data.get('comment', ''),
        total_amount=total_amount,
        status='created'
    )
    # Сохраняем товары из корзины в OrderItem
    order_items = []
    for item in cart_items:
        order_item = OrderItem(
            order=order,
            product=item.product,
            name=item.product.name,
            price=item.product.price,
            quantity=item.quantity,
            total_price=item.total_price
        )
        order_items.append(order_item)
    # Массовое создание — быстрее
    OrderItem.objects.bulk_create(order_items)
    # Удаление товаров
    cart_items.delete()
    if data.get('payment_method') == 'card':
        # Создаём платёж в YooKassa
        try:
            payment = Payment.create({
                "amount": {
                    "value": f"{total_amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "http://127.0.0.1:8000/cart/"
                },
                "capture": True,
                "description": f"Заказ №{order.id}",
                "metadata": {
                    "order_id": order.id
                }
            })

            order.yookassa_payment_id = payment.id
            order.status = payment.status
            order.save()

            return Response({
                "success": True,
                "payment_url": payment.confirmation.confirmation_url
            })

        except Exception as e:
            print("YooKassa error:", str(e))
            logger.error(f"YooKassa error: {str(e)}")
            order.status = 'cancelled'
            order.save()
            return Response({"error": "Ошибка при создании платежа"}, status=500)

    elif data.get('payment_method') == 'cash':
        order.status = 'created'
        order.save()
        Basket.objects.filter(user=user).delete()
        # Можно отправить email, уведомление в Telegram и т.д.
        return Response({
            "success": True,
            "redirect_url": f"/order/success/{order.id}/",
            "message": "Заказ оформлен! Оплата наличными при получении.",
            "order_id": order.id
        })

    else:
        return Response({"error": "Неверный способ оплаты"}, status=400)


@csrf_exempt
def yookassa_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event = data.get('event')

            if event == 'payment.succeeded':
                payment = data['object']
                payment_id = payment['id']
                metadata = payment['metadata']
                order_id = metadata.get('order_id')

                try:
                    order = Order.objects.get(yookassa_payment_id=payment_id)
                    order.status = 'succeeded'
                    order.save()

                    # ✅ Очищаем корзину пользователя
                    Basket.objects.filter(user=order.user).delete()
                    logger.info(f"Корзина очищена для пользователя {order.user} после оплаты заказа {order.id}")

                except Order.DoesNotExist:
                    logger.warning(f"Order not found for payment_id: {payment_id}")

            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return HttpResponse(status=400)
    return HttpResponse(status=400)


@csrf_exempt
@login_required
def add_to_favorites(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
            return JsonResponse({
                'status': 'added' if created else 'already_exists',
                'message': 'Товар добавлен в избранное'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
@csrf_exempt
@login_required
def remove_from_favorites(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            Favorite.objects.filter(user=request.user, product=product).delete()
            return JsonResponse({
                'status': 'removed',
                'message': 'Товар удалён из избранного'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
from django.middleware.csrf import get_token
@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    # Здесь логика для страницы "Избранное"
    return render(request, 'store/category/myfavorite.html',{
        'favorites': favorites,
        'csrf_token': get_token(request)
    })


def radio(request):
    return render(request, 'info/radio.html')


def currency(request):
    return render(request, 'info/currency.html')


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


@api_view(['GET'])
def cart_api(request):
    cart_items = Basket.objects.filter(user=request.user)
    serializer = CartItemSerializer(cart_items, many=True)
    return Response(serializer.data)


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
