from rest_framework.test import APITestCase
from apps.accounts.auth import Authentication
from apps.accounts.models import Otp
from unittest import mock

from apps.accounts.test_utils import TestAccountUtil
from apps.common.exceptions import ErrorCode

class TestAccounts(APITestCase):
    google_login_url = "/api/v1/auth/google/"
    facebook_login_url = "/api/v1/auth/facebook/"
    refresh_url = "/api/v1/auth/refresh/"
    logout_url = "/api/v1/auth/logout/"

    def setUp(self):
        self.new_user = TestAccountUtil.new_user()
        verified_user = TestAccountUtil.verified_user()
        self.verified_user = verified_user

    def test_google_login(self):
        new_user = self.new_user

        # Test for invalid credentials
        response = self.client.post(
            self.login_url,
            {"email": "invalid@email.com", "password": "invalidpassword"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "code": ErrorCode.INVALID_CREDENTIALS,
                "message": "Invalid credentials",
            },
        )

        # Test for unverified credentials (email)
        response = self.client.post(
            self.login_url,
            {"email": new_user.email, "password": "testpassword"},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "code": ErrorCode.UNVERIFIED_USER,
                "message": "Verify your email first",
            },
        )

        # Test for valid credentials and verified email address
        new_user.is_email_verified = True
        new_user.save()
        response = self.client.post(
            self.login_url,
            {"email": new_user.email, "password": "testpassword"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Login successful",
                "data": {"access": mock.ANY, "refresh": mock.ANY},
            },
        )

    def test_refresh_token(self):
        verified_user = self.verified_user
        verified_user.refresh = Authentication.create_refresh_token()
        verified_user.save()

        # Test for invalid refresh token (invalid or expired)
        response = self.client.post(
            self.refresh_url, {"refresh": "invalid_refresh_token"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "code": ErrorCode.INVALID_TOKEN,
                "message": "Refresh token is invalid or expired",
            },
        )

        # Test for valid refresh token
        mock.patch("apps.accounts.auth.Authentication.decode_jwt", return_value=True)
        response = self.client.post(
            self.refresh_url, {"refresh": verified_user.refresh}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "status": "success",
                "message": "Tokens refresh successful",
                "data": {"access": mock.ANY, "refresh": mock.ANY},
            },
        )

    def test_logout(self):
        auth_token = TestAccountUtil.auth_token(self.verified_user)

        # Ensures if authorized user logs out successfully
        bearer = {"HTTP_AUTHORIZATION": f"Bearer {auth_token}"}
        response = self.client.get(self.logout_url, **bearer)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "success", "message": "Logout successful"},
        )

        # Ensures if unauthorized user cannot log out
        self.bearer = {"HTTP_AUTHORIZATION": f"invalid_token"}
        response = self.client.get(self.logout_url, **self.bearer)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "code": ErrorCode.INVALID_TOKEN,
                "message": "Auth Token is Invalid or Expired!",
            },
        )