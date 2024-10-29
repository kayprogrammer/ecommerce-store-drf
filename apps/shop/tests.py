from rest_framework.test import APITestCase

from apps.accounts.test_utils import TestAccountUtil
from apps.shop.test_utils import TestShopUtil

class TestShop(APITestCase):
    product_categories_url = "/api/v1/shop/categories/"

    def setUp(self):
        self.user = TestAccountUtil.new_user()
        self.category = TestShopUtil.category()

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
                "data": [{"name": category.name, "slug": category.slug, "image": category.image_url}],
            },
        )