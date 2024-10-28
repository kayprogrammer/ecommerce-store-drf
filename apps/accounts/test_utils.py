# Test Utils
from django.conf import settings
from apps.accounts.auth import Authentication
from apps.accounts.models import User


class TestAccountUtil:
    def new_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Name",
            "email": "test@example.com",
            "password": settings.SOCIAL_SECRET,
        }
        user = User.objects.create_user(**user_dict)
        return user

    def another_user():
        create_user_dict = {
            "first_name": "Another",
            "last_name": "TestUser",
            "email": "anothertestuser@example.com",
            "password": settings.SOCIAL_SECRET,
        }
        user = User.objects.create_user(**create_user_dict)
        return user

    def auth_token(user):
        user.access = Authentication.create_access_token(user.id)
        user.refresh = Authentication.create_refresh_token()
        user.save()
        return user.access