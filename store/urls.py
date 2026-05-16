from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('products/', views.ProductsListView.as_view(), name='products'),
    path('order/', views.order_view, name='order'),
    path('filters/', views.filter_page, name='filter_page'),
    path('cart/', views.cart, name='cart'),
    path('api/cart/', views.cart_api, name='cart_api'),
    path('api/order/', views.create_order, name='create_order'),
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
