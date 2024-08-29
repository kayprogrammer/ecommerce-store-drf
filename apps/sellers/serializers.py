from rest_framework import serializers
from apps.sellers.choices import (
    BUSINESS_TYPE_CHOICES,
    PREFERRED_SHIPPING_METHOD_CHOICES,
)
from apps.shop.validators import PHONE_REGEX_VALIDATOR


class SellerApplicationSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone_number = serializers.CharField(
        max_length=20, validators=[PHONE_REGEX_VALIDATOR]
    )
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    business_name = serializers.CharField(max_length=255)
    business_type = serializers.ChoiceField(choices=BUSINESS_TYPE_CHOICES)
    business_registration_number = serializers.CharField(max_length=50)
    tax_identification_number = serializers.CharField(max_length=50)
    website_url = serializers.URLField(required=False, allow_null=True)
    business_description = serializers.CharField()

    business_address = serializers.CharField(max_length=255)
    city = serializers.CharField(max_length=100)
    state_province = serializers.CharField(max_length=100)
    postal_code = serializers.CharField(max_length=20)
    country = serializers.CharField(max_length=100)

    bank_name = serializers.CharField(max_length=255)
    bank_account_number = serializers.CharField(max_length=50)
    bank_routing_number = serializers.CharField(max_length=50)
    account_holder_name = serializers.CharField(max_length=255)

    government_id = serializers.FileField(required=False)
    proof_of_address = serializers.FileField(required=False)
    business_license = serializers.FileField(required=False, allow_null=True)

    product_categories = serializers.ListField(
        child=serializers.CharField(), min_length=1, source="product_categories.name"
    )
    expected_sales_volume = serializers.CharField(max_length=50)
    preferred_shipping_method = serializers.ChoiceField(
        choices=PREFERRED_SHIPPING_METHOD_CHOICES
    )
    additional_comments = serializers.CharField(required=False, allow_null=True)

    agree_to_terms = serializers.BooleanField()

    is_approved = serializers.BooleanField(read_only=True)
    application_date = serializers.DateTimeField(read_only=True, source="created_at")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["product_categories"] = instance.product_categories_
        return representation

    @property
    def validated_data(self):
        data = super().validated_data
        product_categories = data["product_categories"]["name"]
        # This is for fixing a swagger issue. It returns list items as ['Cars,Shoes'] instead of ['Cars', 'Shoes']
        # A normal consuming of the api won't have such problem
        if len(product_categories) == 1 and "," in product_categories[0]:
            data["product_categories"]["name"] = product_categories[0].split(",")
        return data
