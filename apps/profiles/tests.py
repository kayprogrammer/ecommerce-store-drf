from rest_framework.test import APITestCase

from apps.accounts.test_utils import TestAccountUtil


class TestProfiles(APITestCase):
    base_url = "/api/v1/profiles"

    maxDiff = None

    def setUp(self):
        self.user = TestAccountUtil.new_user()
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
