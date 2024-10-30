from unittest import mock
from rest_framework.test import APITestCase

from apps.accounts.test_utils import TestAccountUtil
from apps.common.exceptions import ErrorCode
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

        auth_token = TestAccountUtil.auth_token(self.user)
        self.bearer = {"HTTP_AUTHORIZATION": f"Bearer {auth_token}"}

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
                    "products": [TestShopUtil.product_data(product)],
                },
            },
        )

    def check_product_not_found_error(self, response, guest=True):
        self.assertEqual(response.status_code, 404)
        expected_data = {
            "status": "failure",
            "code": ErrorCode.NON_EXISTENT,
            "message": "Product does not exist!",
        }
        if guest:
            expected_data["guest_id"] = mock.ANY
        self.assertEqual(response.json(), expected_data)

    def test_product_details_fetch_successfully(self):
        product = self.product

        # Test for Product not found
        response = self.client.get(f"{self.products_url}invalid_slug/")
        self.check_product_not_found_error(response)

        # Test for product found
        response = self.client.get(f"{self.products_url}{product.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Product Details Fetched Successfully",
                "guest_id": mock.ANY,
                "data": TestShopUtil.product_data(product)
                | {"reviews": mock.ANY, "related_products": mock.ANY},
            },
        )

    def test_write_review(self):
        review_data = {"rating": 5, "text": "This is a good product"}
        # Test for non existent product error
        response = self.client.post(
            f"{self.products_url}invalid_slug/", review_data, **self.bearer
        )
        self.check_product_not_found_error(response, False)

        # Test for success
        response = self.client.post(
            f"{self.products_url}{self.product.slug}/", review_data, **self.bearer
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Review Created successfully",
                "data": {
                    "user": mock.ANY,
                    "rating": review_data["rating"],
                    "text": review_data["text"],
                    "created_at": mock.ANY,
                    "updated_at": mock.ANY,
                },
            },
        )
