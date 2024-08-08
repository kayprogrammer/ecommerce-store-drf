from rest_framework import serializers

from apps.common.serializers import (
    PaginatedResponseDataSerializer,
)
from apps.shop.choices import RATING_CHOICES
from apps.shop.models import Product


class UserSerializer(serializers.Serializer):
    name = serializers.CharField(source="full_name")
    avatar = serializers.CharField(source="avatar_url")


class CategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()
    image = serializers.CharField(source="image_url")


class ProductSerializer(serializers.Serializer):
    seller = UserSerializer()
    name = serializers.CharField()
    slug = serializers.SlugField()
    desc = serializers.CharField()
    price_old = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_current = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = CategorySerializer()
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField()
    avg_rating = serializers.FloatField()
    wishlisted = serializers.BooleanField()
    image1 = serializers.CharField(source="image1_url")
    image2 = serializers.CharField(source="image2_url")
    image3 = serializers.CharField(source="image3_url")

    def get_sizes(self, obj: Product):
        return [size.value for size in obj.sizes.all()]

    def get_colors(self, obj: Product):
        return [color.value for color in obj.colors.all()]


class ProductsResponseDataSerializer(PaginatedResponseDataSerializer):
    products = ProductSerializer(many=True, source="items")


class ReviewSerializer(serializers.Serializer):
    user = UserSerializer(read_only=True)
    rating = serializers.ChoiceField(choices=RATING_CHOICES)
    text = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ReviewResponseDataSerializer(PaginatedResponseDataSerializer):
    items = ReviewSerializer(many=True)


class ProductDetailSerializer(ProductSerializer):
    related_products = ProductSerializer(many=True)
    reviews = ReviewResponseDataSerializer(source="reviews_data")


class OrderItemProductSerializer(serializers.Serializer):
    seller = UserSerializer()
    name = serializers.CharField()
    slug = serializers.SlugField()
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="price_current"
    )


class OrderItemSerializer(serializers.Serializer):
    product = OrderItemProductSerializer()
    quantity = serializers.IntegerField()
    size = serializers.CharField(source="size.value")
    color = serializers.CharField(source="color.value")
    total = serializers.FloatField(source="get_total")


class OrderItemsResponseDataSerializer(PaginatedResponseDataSerializer):
    items = OrderItemSerializer(many=True)


class ToggleCartItemSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    quantity = serializers.IntegerField(min_value=0)
    size = serializers.CharField(required=False)
    color = serializers.CharField(required=False)

class CheckoutSerializer(serializers.Serializer):
    coupon = serializers.CharField(required=False)
    