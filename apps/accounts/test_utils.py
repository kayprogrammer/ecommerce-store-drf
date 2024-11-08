# Test Utils
from datetime import UTC, datetime
from django.conf import settings
from apps.accounts.auth import Authentication
from apps.accounts.models import User
from django.contrib.auth.hashers import make_password

from apps.sellers.models import Seller
from apps.shop.models import Category, Country


class TestAccountUtil:
    def new_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Name",
            "email": "test@example.com",
            "password": make_password(settings.SOCIAL_SECRET),
        }
        user, _ = User.objects.get_or_create(
            email=user_dict["email"], defaults=user_dict
        )
        return user

    def another_user():
        create_user_dict = {
            "first_name": "Another",
            "last_name": "TestUser",
            "email": "anothertestuser@example.com",
            "password": make_password(settings.SOCIAL_SECRET),
        }
        user, _ = User.objects.get_or_create(
            email=create_user_dict["email"], defaults=create_user_dict
        )
        return user

    def country():
        country, _ = Country.objects.get_or_create(
            name="TestCountry", code="TC", phone_code="+123"
        )
        return country

    def new_seller():
        user_dict = {
            "first_name": "Test",
            "last_name": "Seller",
            "email": "testseller@example.com",
            "password": make_password(settings.SOCIAL_SECRET),
            "account_type": "SELLER",
        }
        user, _ = User.objects.get_or_create(
            email=user_dict["email"], defaults=user_dict
        )
        seller_dict = {
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": "+2341234567",
            "date_of_birth": datetime.now(UTC),
            "business_name": f"{user.full_name}'s Ventures",
            "business_type": "sole_proprietorship",
            "business_registration_number": "32435456",
            "tax_identification_number": "343354543",
            "business_description": "My good business",
            "business_address": "123, Noman street",
            "city": "Lekki",
            "state_province": "Lagos",
            "postal_code": "123234",
            "country": TestAccountUtil.country(),
            "bank_name": "Cool namk",
            "bank_account_number": "234345456",
            "bank_routing_number": "83242842834",
            "account_holder_name": user.full_name,
            "agree_to_terms": True,
            "expected_sales_volume": "2000",
            "preferred_shipping_method": "standard",
            "is_approved": True,
        }
        seller, _ = Seller.objects.get_or_create(user=user, defaults=seller_dict)
        category, _ = Category.objects.get_or_create(name="Test Category")
        seller.product_categories.add(category)
        return seller

    def auth_token(user):
        user.access = Authentication.create_access_token(user.id)
        user.refresh = Authentication.create_refresh_token()
        user.save()
        return user.access
