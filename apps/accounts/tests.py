from rest_framework.test import APITestCase
from apps.accounts.auth import Authentication
from unittest import mock

from apps.accounts.test_utils import TestAccountUtil
from apps.common.exceptions import ErrorCode


class TestAccounts(APITestCase):
    google_login_url = "/api/v1/auth/google/"
    facebook_login_url = "/api/v1/auth/facebook/"
    refresh_url = "/api/v1/auth/refresh/"
    logout_url = "/api/v1/auth/logout/"

    def setUp(self):
        self.user = TestAccountUtil.new_user()

    def test_google_login(self):
        # Test for invalid token
        with mock.patch("apps.accounts.auth.Google.validate") as mock_function:
            mock_function.return_value = (
                None,
                ErrorCode.INVALID_TOKEN,
                "Invalid Auth Token",
            )
            response = self.client.post(
                self.google_login_url,
                {"token": "invalid_token"},
            )
            self.assertEqual(response.status_code, 401)
            self.assertEqual(
                response.json(),
                {
                    "status": "failure",
                    "code": ErrorCode.INVALID_TOKEN,
                    "message": "Invalid Auth Token",
                },
            )

        # Test for valid token
        with mock.patch("apps.accounts.auth.Google.validate") as mock_function:
            expected_id_info = {
                "name": "Test GoogleUser",
                "email": "testgoogleuser@gmail.com",
                "picture": "https://img.com",
            }
            mock_function.return_value = (expected_id_info, None, None)
            response = self.client.post(
                self.google_login_url,
                {"token": "token"},
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                response.json(),
                {
                    "status": "success",
                    "message": "Tokens Generation successful",
                    "data": {"access": mock.ANY, "refresh": mock.ANY},
                },
            )

    def test_facebook_login(self):
        # Test for invalid token
        with mock.patch("apps.accounts.auth.Facebook.validate") as mock_function:
            mock_function.return_value = (
                None,
                ErrorCode.INVALID_TOKEN,
                "Invalid Auth Token",
            )
            response = self.client.post(
                self.facebook_login_url,
                {"token": "invalid_token"},
            )
            self.assertEqual(response.status_code, 401)
            self.assertEqual(
                response.json(),
                {
                    "status": "failure",
                    "code": ErrorCode.INVALID_TOKEN,
                    "message": "Invalid Auth Token",
                },
            )

        # Test for valid token
        with mock.patch("apps.accounts.auth.Facebook.validate") as mock_function:
            expected_id_info = {
                "name": "Test FacebookUser",
                "email": "testfacebookuser@gmail.com",
                "picture": "https://img.com",
            }
            mock_function.return_value = (expected_id_info, None, None)
            response = self.client.post(
                self.facebook_login_url,
                {"token": "token"},
            )
            self.assertEqual(response.status_code, 201)
            self.assertEqual(
                response.json(),
                {
                    "status": "success",
                    "message": "Tokens Generation successful",
                    "data": {"access": mock.ANY, "refresh": mock.ANY},
                },
            )

    def test_refresh_token(self):
        user = self.user
        user.refresh = Authentication.create_refresh_token()
        user.save()

        # Test for invalid refresh token (invalid or expired)
        response = self.client.post(
            self.refresh_url, {"token": "invalid_refresh_token"}
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
        response = self.client.post(self.refresh_url, {"token": user.refresh})
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
        auth_token = TestAccountUtil.auth_token(self.user)

        # Ensures if authorized user logs out successfully
        bearer = {"HTTP_AUTHORIZATION": f"Bearer {auth_token}"}
        response = self.client.get(self.logout_url, **bearer)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "success", "message": "Logout successful"},
        )

        # Ensures if unauthorized user cannot log out
        bearer = {"HTTP_AUTHORIZATION": f"invalid_token"}
        response = self.client.get(self.logout_url, **bearer)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {
                "status": "failure",
                "code": ErrorCode.INVALID_TOKEN,
                "message": "Access Token is Invalid or Expired!",
            },
        )
