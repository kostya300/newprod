# newprod/api/urls.py
from django.urls import path, include
from rest_framework import routers
from users.api.views import UserViewSet
from store.api.views import ProductViewSet
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
#Импорты для rate limiting
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
# Определение защищённого view ДО urlpatterns
@method_decorator(ratelimit(key='ip', rate='3/m', method='POST', block=True), name='post')
class RateLimitedTokenObtainPairView(TokenObtainPairView):
    """
    JWT login с ограничением: 3 попытки в минуту с одного IP
    """
    pass
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # 🔐 JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Опционально: сессии
    path('auth/', include('rest_framework.urls')),

# 📄 Документация API
    path('schema/', SpectacularAPIView.as_view(), name='schema'),  # JSON-схема
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Swagger UI
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # Redoc

    # Опционально: сессии для браузера
    path('auth/', include('rest_framework.urls')),

]
