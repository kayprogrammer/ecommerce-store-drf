from autoslug import AutoSlugField
from django.db import models

from apps.accounts.models import User
from apps.common.models import BaseModel
from apps.sellers.choices import (
    BUSINESS_TYPE_CHOICES,
    PREFERRED_SHIPPING_METHOD_CHOICES,
)
from apps.shop.models import Category, Country


class Seller(BaseModel):
    # Link to the User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller")

    # Personal Information
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)

    # Business Information
    business_name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="business_name", always_update=True, null=True)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPE_CHOICES)
    business_registration_number = models.CharField(max_length=50)
    tax_identification_number = models.CharField(max_length=50)
    website_url = models.URLField(null=True, blank=True)
    business_description = models.TextField()

    # Address Information
    business_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)

    # Bank Information
    bank_name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=50)
    bank_routing_number = models.CharField(max_length=50)
    account_holder_name = models.CharField(max_length=255)

    # Identity Verification
    government_id = models.FileField(upload_to="sellers/government_ids/")
    proof_of_address = models.FileField(upload_to="sellers/proof_of_address/")
    business_license = models.FileField(
        upload_to="sellers/business_licenses/", null=True, blank=True
    )

    # Product Information
    product_categories = models.ManyToManyField(Category)

    # Additional Information
    expected_sales_volume = models.CharField(max_length=50)
    preferred_shipping_method = models.CharField(
        max_length=20, choices=PREFERRED_SHIPPING_METHOD_CHOICES
    )
    additional_comments = models.TextField(null=True, blank=True)

    # Agreement
    agree_to_terms = models.BooleanField(default=False)

    # Status fields
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Seller for {self.business_name} by {self.full_name}"
