"""
URL configuration for newprod project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('rest_framework.urls', namespace='api_drf')),
    path('store/', include('store.urls')),
    path('users/', include('users.urls', namespace='users')),

    path('', include("store.urls")),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('api/', include('newprod.api.urls')),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('orders/history/', views.order_history, name='order_history'),
    path('api/order/', views.create_order, name='create_order'),
    path('api/yookassa-webhook/', views.yookassa_webhook, name='yookassa_webhook'),
    path('orders/<int:order_id>/', views.about_order, name='about_order'),

]
# Подключение медиа-файлов только в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
