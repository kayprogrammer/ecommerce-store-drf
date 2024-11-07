from rest_framework import serializers

from apps.common.serializers import PaginatedResponseDataSerializer
from apps.shop.serializers import OrderSerializer, ShippingAddressSerializer


class ProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=25)
    last_name = serializers.CharField(max_length=25)
    email = serializers.CharField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(write_only=True, required=False)
    account_type = serializers.CharField(read_only=True)


class ShippingAddressSerializerWithID(ShippingAddressSerializer):
    id = serializers.UUIDField(read_only=True)


class OrdersResponseDataSerializer(PaginatedResponseDataSerializer):
    orders = OrderSerializer(many=True, source="items")
