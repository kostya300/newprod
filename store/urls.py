from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('products/', views.products, name='products'),

    path('filters/', views.filter_page, name='filter_page'),
    path('cart/', views.cart, name='cart'),
    path('baskets/add/<int:product_id>/', views.basket_add, name='basket_add'),
    path('baskets/add-one/<int:item_id>/', views.basket_add_one, name='basket_add_one'),
    path('baskets/remove-one/<int:item_id>/', views.basket_remove_one, name='basket_remove_one'),
    path('baskets/remove/<int:item_id>/', views.basket_remove, name='basket_remove'),
    path('product_detail/<slug:slug>/', views.product_detail, name='product_detail'),
    path('contacts/', views.contacts, name='contacts'),
    path('favorites/', views.my_favorites, name='favorites'),
    path('api/ai/chat/', views.ai_chat, name='ai_chat'),
    path('radio/', views.radio, name='radio'),
    path('goods-online/', views.goods_for_internet, name='goods_for_internet'),
    path('api/ai-internet-goods/', views.ai_internet_goods, name='ai_internet_goods'),

]
