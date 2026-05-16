from rest_framework import serializers
from .models import Basket, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image']
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = Basket
        fields = ['id', 'product', 'quantity', 'total_price']
    def get_total_price(self, obj):
        return obj.quantity * obj.product.price