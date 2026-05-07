# store/api/views.py
from rest_framework import viewsets
from ..models import Product
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(in_stock=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filterset_fields = ['category']  # ← убрали 'brand'
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']