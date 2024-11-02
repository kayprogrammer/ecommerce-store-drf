from rest_framework import serializers

from apps.common.serializers import (
    PaginatedResponseDataSerializer,
)
from apps.shop.choices import PAYMENT_GATEWAY_CHOICES, RATING_CHOICES
from apps.shop.models import Product
from apps.shop.validators import PHONE_REGEX_VALIDATOR


class UserSerializer(serializers.Serializer):
    name = serializers.CharField(source="full_name")
    avatar = serializers.CharField(source="avatar_url")


class SellerSerializer(serializers.Serializer):
    name = serializers.CharField(source="business_name")
    slug = serializers.CharField()
    avatar = serializers.CharField(source="user.avatar_url")


class CategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()
    image = serializers.CharField(source="image_url")


class ProductSerializer(serializers.Serializer):
    seller = SellerSerializer()
    name = serializers.CharField()
    slug = serializers.SlugField()
    desc = serializers.CharField()
    price_old = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_current = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = CategorySerializer()
    sizes = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField(default=0)
    avg_rating = serializers.FloatField(default=0)
    wishlisted = serializers.BooleanField(default=False)
    image1 = serializers.CharField(source="image1_url")
    image2 = serializers.CharField(source="image2_url")
    image3 = serializers.CharField(source="image3_url")

    def get_sizes(self, obj: Product):
        sizes = obj.sizes_ if hasattr(obj, "sizes_") and obj.sizes_ else obj.sizes.all()
        return [size.value for size in sizes]

    def get_colors(self, obj: Product):
        colors = (
            obj.colors_ if hasattr(obj, "colors_") and obj.colors_ else obj.colors.all()
        )
        return [color.value for color in colors]


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
    seller = SellerSerializer()
    name = serializers.CharField()
    slug = serializers.SlugField()
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="price_current"
    )


class OrderItemSerializer(serializers.Serializer):
    product = OrderItemProductSerializer()
    quantity = serializers.IntegerField()
    size = serializers.CharField(source="size.value", allow_null=True)
    color = serializers.CharField(source="color.value", allow_null=True)
    total = serializers.FloatField(source="get_total")


class OrderItemsResponseDataSerializer(PaginatedResponseDataSerializer):
    items = OrderItemSerializer(many=True)


class ToggleCartItemSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    quantity = serializers.IntegerField(min_value=0)
    size = serializers.CharField(required=False)
    color = serializers.CharField(required=False)


class CountrySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    code = serializers.CharField(max_length=20)
    phone_code = serializers.CharField(max_length=20)


class ShippingAddressSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=500)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, validators=[PHONE_REGEX_VALIDATOR])
    address = serializers.CharField(max_length=1000)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    country = serializers.CharField()
    zipcode = serializers.IntegerField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Check if `country` is a related field (e.g., `country.name`)
        if hasattr(instance, "country") and hasattr(instance.country, "name"):
            representation["country"] = instance.country.name
        else:
            # Handle the case where `country` is a direct string field
            representation["country"] = (
                instance.country if hasattr(instance, "country") else None
            )

        return representation


class CheckoutSerializer(serializers.Serializer):
    shipping_id = serializers.UUIDField(required=False)
    coupon = serializers.CharField(required=False)
    shipping = ShippingAddressSerializer(required=False)
    payment_method = serializers.ChoiceField(choices=PAYMENT_GATEWAY_CHOICES)

    def validate(self, attrs):
        shipping_id = attrs.get("shipping_id")
        shipping = attrs.get("shipping")
        if shipping_id and shipping:
            raise serializers.ValidationError(
                {"shipping": "Cannot set shipping if shipping_id has been set!"}
            )
        if not shipping_id and not shipping:
            raise serializers.ValidationError(
                {"shipping_id": "Set shipping_id or shipping!"}
            )
        return attrs


class OrderSerializer(serializers.Serializer):
    tx_ref = serializers.CharField()
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    delivery_status = serializers.CharField()
    payment_status = serializers.CharField()
    payment_method = serializers.CharField()
    coupon = serializers.CharField(source="coupon.code", required=False)
    date_delivered = serializers.DateTimeField()
    shipping_details = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(
        max_digits=100, decimal_places=2, source="get_cart_subtotal"
    )
    shipping_fee = serializers.DecimalField(max_digits=100, decimal_places=2)
    total = serializers.DecimalField(
        max_digits=100, decimal_places=2, source="get_cart_total"
    )

    def get_shipping_details(self, obj):
        return ShippingAddressSerializer(obj).data
