from apps.accounts.test_utils import TestAccountUtil
from apps.shop.models import Category, Product


class TestShopUtil:
    def category():
        category, _ = Category.objects.get_or_create(name="Test Category")
        return category

    def product():
        seller = TestAccountUtil.new_seller()
        product_data = {
            "desc": "My good product",
            "price_old": 1000.25,
            "price_current": 900.25,
            "category": TestShopUtil.category(),
        }
        product, _ = Product.objects.get_or_create(
            seller=seller, name="Test Product", defaults=product_data
        )
        return product
