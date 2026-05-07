# store/api/serializers.py
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from ..models import Product

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'image', 'category', 'category_name',
            'in_stock', 'is_new', 'is_featured',
            'rating', 'review_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    @extend_schema_field(str)
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        return None

    image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'image', 'category', 'category_name',
            'in_stock', 'is_new', 'is_featured',
            'rating', 'review_count', 'created_at', 'updated_at'
        ]