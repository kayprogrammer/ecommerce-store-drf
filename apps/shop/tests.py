from unittest import mock
from rest_framework.test import APITestCase

from apps.accounts.test_utils import TestAccountUtil
from apps.shop.test_utils import TestShopUtil


class TestShop(APITestCase):
    base_url = "/api/v1/shop"
    product_categories_url = f"{base_url}/categories/"
    products_url = f"{base_url}/products/"

    maxDiff = None

    def setUp(self):
        self.user = TestAccountUtil.new_user()
        self.category = TestShopUtil.category()
        self.product = TestShopUtil.product()

    def test_categories_fetch(self):
        category = self.category

        response = self.client.get(
            self.product_categories_url,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Categories fetched successfully",
                "data": [
                    {
                        "name": category.name,
                        "slug": category.slug,
                        "image": category.image_url,
                    }
                ],
            },
        )

    def test_products_fetch(self):
        product = self.product
        category = self.category

        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Products Fetched Successfully",
                "guest_id": mock.ANY,
                "data": {
                    "current_page": 1,
                    "last_page": 1,
                    "per_page": 100,
                    "products": [
                        {
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
                            "sizes": [],
                            "colors": [],
                            "reviews_count": 0,
                            "avg_rating": 0,
                            "wishlisted": False,
                            "image1": None,
                            "image2": None,
                            "image3": None,
                        }
                    ],
                },
            },
        )
