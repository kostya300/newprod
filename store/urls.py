from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path("register/", views.register_view, name="register"),
    path('products/', views.products, name='products'),
    path('cart/', views.cart, name='cart'),
    path('product_detail', views.product_detail, name='product_detail'),
    path('contacts/', views.contacts, name='contacts'),
]
