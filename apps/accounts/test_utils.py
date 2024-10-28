# Test Utils
from apps.accounts.auth import Authentication
from apps.accounts.models import User


class TestAccountUtil:
    def new_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Name",
            "email": "test@example.com",
            "password": "testpassword",
        }
        user = User.objects.create_user(**user_dict)
        return user

    def verified_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Verified",
            "email": "testverifieduser@example.com",
            "is_email_verified": True,
            "password": "testpassword",
        }
        user = User.objects.create_user(**user_dict)
        return user

    def another_verified_user():
        create_user_dict = {
            "first_name": "AnotherTest",
            "last_name": "UserVerified",
            "email": "anothertestverifieduser@example.com",
            "is_email_verified": True,
            "password": "anothertestverifieduser123",
        }
        user = User.objects.create_user(**create_user_dict)
        return user

    def auth_token(verified_user):
        verified_user.access = Authentication.create_access_token(verified_user.id)
        verified_user.refresh = Authentication.create_refresh_token()
        verified_user.save()
        return verified_user.access