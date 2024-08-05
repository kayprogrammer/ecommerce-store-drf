from rest_framework import serializers


class SellerSerializer(serializers.Serializer):
    name = serializers.CharField(source="full_name")
    avatar = serializers.CharField(source="avatar_url")


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
    sizes = serializers.ListField(source="value")
    colors = serializers.ListField(source="value")
    image1 = serializers.CharField()
    image2 = serializers.CharField()
    image3 = serializers.CharField()
