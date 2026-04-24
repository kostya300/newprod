from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('products/', views.products, name='products'),
    path('filters/', views.filter_page, name='filter_page'),
    path('cart/', views.cart, name='cart'),
    path('product_detail/<slug:slug>/', views.product_detail, name='product_detail'),
    path('contacts/', views.contacts, name='contacts'),
    path('favorites/', views.my_favorites, name='favorites'),

]
