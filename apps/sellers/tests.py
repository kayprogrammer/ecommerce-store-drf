from django.test import override_settings
from rest_framework.test import APITestCase

from apps.accounts.test_utils import TestAccountUtil
from apps.common.exceptions import ErrorCode
from apps.profiles.test_utils import TestProfileUtil
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.shop.models import Color, Product, Size
from apps.shop.test_utils import TestShopUtil
from PIL import Image
from io import BytesIO


@override_settings(
    STORAGES={"default": {"BACKEND": "apps.common.utils.InMemoryStorage"}}
)
class TestSeller(APITestCase):
    base_url = "/api/v1/sellers"
    apply_url = f"{base_url}/apply/"
    products_url = f"{base_url}/products/"
    orders_url = f"{base_url}/orders/"

    maxDiff = None

    def setUp(self):
        self.user = TestAccountUtil.new_user()
        self.seller = TestAccountUtil.new_seller()
        self.product = TestShopUtil.product()
        self.category = TestShopUtil.category()
        self.order = TestProfileUtil.order(self.user)

        auth_token = TestAccountUtil.auth_token(self.user)
        self.bearer = {"HTTP_AUTHORIZATION": f"Bearer {auth_token}"}
        seller_auth_token = TestAccountUtil.auth_token(self.seller.user)
        self.seller_bearer = {"HTTP_AUTHORIZATION": f"Bearer {seller_auth_token}"}

    def create_test_image(
        self, name="test_image.jpg", size=(100, 100), color=(255, 0, 0)
    ):
        # Create an image with Pillow
        image = Image.new("RGB", size, color)
        image_file = BytesIO()
        image.save(image_file, format="JPEG")
        image_file.seek(0)
        return SimpleUploadedFile(name, image_file.read(), content_type="image/jpeg")

    def get_application_data(self):
        return {
            "full_name": "Jane Doe",
            "email": "janedoe@example.com",
            "phone_number": "+1234567890",
            "date_of_birth": "1990-05-20",
            "business_name": "Doe Enterprises",
            "business_type": "sole_proprietorship",
            "business_registration_number": "12345678",
            "tax_identification_number": "TIN123456789",
            "website_url": "https://doeenterprises.com",
            "business_description": "We sell high-quality goods worldwide.",
            "business_address": "123 Main St, Suite 400",
            "city": "Springfield",
            "state_province": "IL",
            "postal_code": "62701",
            "country": "Invalid Country",
            "bank_name": "Global Bank",
            "bank_account_number": "0987654321",
            "bank_routing_number": "111000025",
            "account_holder_name": "Jane Doe",
            "government_id": self.create_test_image(),
            "proof_of_address": self.create_test_image(),
            "product_categories": ["Invalid Category"],
            "expected_sales_volume": "50000-100000",
            "preferred_shipping_method": "standard",
            "additional_comments": "Excited to join this platform!",
            "agree_to_terms": True,
        }

    def test_invalid_country(self):
        data = self.get_application_data()
        response = self.client.post(
            self.apply_url, data=data, format="multipart", **self.bearer
        )
        self.assertEqual(response.status_code, 422)
        result = response.json()
        self.assertEqual(result["status"], "failure")
        self.assertEqual(result["message"], "Invalid Entry")
        self.assertEqual(result["code"], ErrorCode.INVALID_ENTRY)
        self.assertEqual(result["data"], {"country": "Invalid country selected"})

    def test_invalid_category(self):
        data = self.get_application_data()
        data["country"] = TestAccountUtil.country().name  # Valid country
        response = self.client.post(
            self.apply_url, data=data, format="multipart", **self.bearer
        )
        self.assertEqual(response.status_code, 422)
        result = response.json()
        self.assertEqual(result["status"], "failure")
        self.assertEqual(result["code"], ErrorCode.INVALID_ENTRY)
        self.assertEqual(
            result["data"], {"product_categories": "No valid category was selected"}
        )

    def test_successful_application(self):
        data = self.get_application_data()
        data["country"] = TestAccountUtil.country().name  # Valid country
        data["product_categories"] = self.category.name  # valid category

        response = self.client.post(
            self.apply_url, data=data, format="multipart", **self.bearer
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Application submitted successfully")

    def test_invalid_business_name_slug(self):
        response = self.client.get(f"{self.products_url}invalid_slug/", **self.bearer)
        self.assertEqual(response.status_code, 404)
        result = response.json()
        self.assertEqual(result["status"], "failure")
        self.assertEqual(result["code"], ErrorCode.NON_EXISTENT)

    def test_retrieve_seller_products(self):
        response = self.client.get(
            f"{self.products_url}{self.seller.slug}/", **self.bearer
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Seller Products Fetched Successfully")

    def test_product_update(self):
        product = self.product
        data = {"name": "Product updated", "desc": "Product description"}

        response = self.client.patch(
            f"{self.products_url}{product.slug}/",
            data=data,
            format="multipart",
            **self.seller_bearer,
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Product Updated Successfully")

    def test_product_delete(self):
        product = Product.objects.create(
            seller=self.seller,
            name="Test Product",
            desc="Whatever",
            price_old=100.34,
            price_current=92.22,
            category=self.category,
        )
        response = self.client.delete(
            f"{self.products_url}{product.slug}/", **self.seller_bearer
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Product Deleted Successfully")

    def test_product_create(self):
        size = Size.objects.create(value="M")
        color = Color.objects.create(value="Green")

        data = {
            "name": "Product create",
            "desc": "Product description",
            "price_current": 1000.00,
            "category_slug": self.category.slug,
            "sizes": [size.value],
            "colors": [color.value],
            "in_stock": 100,
            "image1": self.create_test_image(),
        }

        response = self.client.post(
            self.products_url, data=data, format="multipart", **self.seller_bearer
        )
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Product created successfully")

    def test_retrieve_orders(self):
        response = self.client.get(self.orders_url, **self.seller_bearer)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Orders Fetched Successfully")
