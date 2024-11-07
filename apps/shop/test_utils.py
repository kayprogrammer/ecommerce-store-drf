from unittest import mock
from apps.accounts.test_utils import TestAccountUtil
from apps.shop.models import Category, OrderItem, Product, Wishlist


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

    def orderitem(order=None):
        user = TestAccountUtil.new_user()
        product = TestShopUtil.product()
        orderitem, _ = OrderItem.objects.get_or_create(
            user=user, product=product, order=order, defaults={"quantity": 1}
        )
        return orderitem

    def product_data(product: Product):
        category = product.category
        return {
            "seller": mock.ANY,
            "name": product.name,
            "slug": product.slug,
            "desc": product.desc,
            "price_old": str(product.price_old),
            "price_current": str(product.price_current),
            "category": {
                "name": category.name,
                "slug": category.slug,
                "image": category.image_url,
            },
            "sizes": list(product.sizes.values_list("value", flat=True)),
            "colors": list(product.colors.values_list("value", flat=True)),
            "reviews_count": mock.ANY,
            "avg_rating": mock.ANY,
            "wishlisted": mock.ANY,
            "image1": product.image1_url,
            "image2": product.image2_url,
            "image3": product.image3_url,
        }

    def wishlist():
        wishlist, _ = Wishlist.objects.get_or_create(
            user=TestAccountUtil.new_user(), product=TestShopUtil.product()
        )
        return wishlist
