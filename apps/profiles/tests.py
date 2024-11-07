from unittest import mock
import uuid
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.accounts.test_utils import TestAccountUtil
from apps.common.exceptions import ErrorCode
from apps.profiles.test_utils import TestProfileUtil


class TestProfiles(APITestCase):
    base_url = "/api/v1/profiles"
    shipping_address_url = f"{base_url}/shipping_addresses/"

    maxDiff = None

    def setUp(self):
        self.user = TestAccountUtil.new_user()
        self.shipping_addr = TestProfileUtil.shipping_address(self.user)
        auth_token = TestAccountUtil.auth_token(self.user)
        self.bearer = {"HTTP_AUTHORIZATION": f"Bearer {auth_token}"}

    def test_retrieve_profile(self):
        user = self.user
        response = self.client.get(f"{self.base_url}/", **self.bearer)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "User Profile Fetched")
        self.assertEqual(
            result["data"],
            {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "account_type": user.account_type,
            },
        )

    def test_update_profile(self):
        user = self.user
        data = {"first_name": "Test", "last_name": "Updated"}
        response = self.client.put(f"{self.base_url}/", data, **self.bearer)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "User Profile Updated")
        self.assertEqual(
            result["data"],
            {
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "email": user.email,
                "avatar_url": user.avatar_url,
                "account_type": user.account_type,
            },
        )

    def test_account_deactivation(self):
        # Setup account to be deactivated
        user = User.objects.create_user(
            first_name="Test",
            last_name="User",
            email="testuser2@example.com",
            password="testpass",
        )
        auth_token = TestAccountUtil.auth_token(user)
        bearer = {"HTTP_AUTHORIZATION": f"Bearer {auth_token}"}

        response = self.client.delete(f"{self.base_url}/", **bearer)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "User Account Deactivated")

    def test_retrieve_shipping_addresses(self):
        addr = self.shipping_addr
        response = self.client.get(
            self.shipping_address_url, **self.bearer
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Shipping addresses returned")
        self.assertEqual(
            result["data"],
            [
                {
                    "full_name": addr.full_name,
                    "email": addr.email,
                    "phone": addr.phone,
                    "address": addr.address,
                    "city": addr.city,
                    "state": addr.state,
                    "country": addr.country.name,
                    "zipcode": int(addr.zipcode),
                    "id": str(addr.id),
                }
            ],
        )

    def test_create_shipping_addresses(self):
        data = {
            "full_name": "Test User",
            "email": "test@eee.com",
            "phone": "+23412345678",
            "address": "123, Whatever street",
            "city": "Lobomo",
            "state": "Leclanche",
            "country": "Invalid country",
            "zipcode": 54321,
        }
        # Check for error response due to invalid country
        response = self.client.post(
            self.shipping_address_url, data, **self.bearer
        )
        self.assertEqual(response.status_code, 422)
        result = response.json()
        self.assertEqual(result["status"], "failure")
        self.assertEqual(result["message"], "Invalid Entry")
        self.assertEqual(result["code"], ErrorCode.INVALID_ENTRY)
        self.assertEqual(result["data"], {"country": "Invalid country selected"})

        # Check for successful creation of shipping address
        data["country"] = TestAccountUtil.country().name
        response = self.client.post(
            self.shipping_address_url, data, **self.bearer
        )
        self.assertEqual(response.status_code, 201)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Shipping address created successfully")
        self.assertEqual(
            result["data"],
            {
                "full_name": data["full_name"],
                "email": data["email"],
                "phone": data["phone"],
                "address": data["address"],
                "city": data["city"],
                "state": data["state"],
                "country": data["country"],
                "zipcode": data["zipcode"],
                "id": mock.ANY,
            },
        )

    def check_addr_not_found_error(self, response):
        self.assertEqual(response.status_code, 404)
        expected_data = {
            "status": "failure",
            "code": ErrorCode.NON_EXISTENT,
            "message": "User does not have a shipping address with that ID",
        }
        self.assertEqual(response.json(), expected_data)

    def test_retrieve_single_shipping_addresses(self):
        addr = self.shipping_addr
        # Test for address not found
        response = self.client.get(f"{self.shipping_address_url}{str(uuid.uuid4())}/", **self.bearer)
        self.check_addr_not_found_error(response)

        # Test for address successfully returned
        response = self.client.get(
            f"{self.shipping_address_url}{str(addr.id)}/", **self.bearer
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Shipping address returned")
        self.assertEqual(
            result["data"],
            {
                "full_name": addr.full_name,
                "email": addr.email,
                "phone": addr.phone,
                "address": addr.address,
                "city": addr.city,
                "state": addr.state,
                "country": addr.country.name,
                "zipcode": int(addr.zipcode),
                "id": str(addr.id),
            },
        )

    def test_update_shipping_address(self):
        data = {
            "full_name": "Test User Updated",
            "email": "testupdated@eaee.com",
            "phone": "+234125678",
            "address": "123, Whatever street updated",
            "city": "City updated",
            "state": "State updated",
            "country": "Invalid country",
            "zipcode": 543221,
        }

        addr = self.shipping_addr
        # Test for address not found
        response = self.client.put(f"{self.shipping_address_url}{str(uuid.uuid4())}/", data, **self.bearer)
        self.check_addr_not_found_error(response)

        # Check for error response due to invalid country
        response = self.client.put(
            self.shipping_address_url, data, **self.bearer
        )
        self.assertEqual(response.status_code, 422)
        result = response.json()
        self.assertEqual(result["status"], "failure")
        self.assertEqual(result["message"], "Invalid Entry")
        self.assertEqual(result["code"], ErrorCode.INVALID_ENTRY)
        self.assertEqual(result["data"], {"country": "Invalid country selected"})

        # Check for successful update of shipping address
        data["country"] = TestAccountUtil.country().name
        response = self.client.put(
            f"{self.shipping_address_url}{addr.id}/", data, **self.bearer
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Shipping address updated successfully")
        self.assertEqual(
            result["data"],
            {
                "full_name": data["full_name"],
                "email": data["email"],
                "phone": data["phone"],
                "address": data["address"],
                "city": data["city"],
                "state": data["state"],
                "country": data["country"],
                "zipcode": data["zipcode"],
                "id": addr.id,
            },
        )