from rest_framework import serializers
from apps.sellers.choices import (
    BUSINESS_TYPE_CHOICES,
    PREFERRED_SHIPPING_METHOD_CHOICES,
)
from apps.shop.validators import PHONE_REGEX_VALIDATOR


class SellerSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone_number = serializers.CharField(
        max_length=20, validators=[PHONE_REGEX_VALIDATOR]
    )
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    business_name = serializers.CharField(max_length=255)
    slug = serializers.CharField(read_only=True)
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

    government_id = serializers.FileField()
    proof_of_address = serializers.FileField()
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


class ProductCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    desc = serializers.CharField()
    price_current = serializers.DecimalField(max_digits=10, decimal_places=2)
    category_slug = serializers.CharField(max_length=200)
    sizes = serializers.ListField(child=serializers.CharField(max_length=5))
    colors = serializers.ListField(child=serializers.CharField(max_length=20))
    in_stock = serializers.IntegerField()
    image1 = serializers.ImageField()
    image2 = serializers.ImageField(required=False)
    image3 = serializers.ImageField(required=False)

    @property
    def validated_data(self):
        data = super().validated_data
        sizes = data["sizes"]
        colors = data["colors"]

        # This is for fixing a swagger issue. It returns list items as ['Cars,Shoes'] instead of ['Cars', 'Shoes']
        # A normal consuming of the api won't have such problem
        if len(sizes) == 1 and "," in sizes[0]:
            data["sizes"] = sizes[0].split(",")
        if len(colors) == 1 and "," in colors[0]:
            data["colors"] = colors[0].split(",")
        return data

    def __init__(self, *args, **kwargs):
        # Detect if this is a partial update (PATCH request)
        partial = kwargs.pop("partial", False)
        super().__init__(*args, **kwargs)

        if partial:
            # Make fields accept blank/empty/null values for PATCH requests
            for _, field in self.fields.items():
                if isinstance(field, serializers.ListField):
                    field.allow_empty = True
                    field.child.allow_blank = True
                field.required = False
