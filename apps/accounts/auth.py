from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
import facebook

from .senders import EmailUtil

from .models import User


class Google:
    """Google class to fetch the user info and return it"""

    @staticmethod
    def validate(auth_token):
        """
        validate method Queries the Google oAUTH2 api to fetch the user info
        """
        try:
            idinfo = id_token.verify_oauth2_token(auth_token, google_requests.Request())

            if "accounts.google.com" in idinfo["iss"]:
                return idinfo

        except:
            return None


class Facebook:
    """
    Facebook class to fetch the user info and return it
    """

    @staticmethod
    def validate(auth_token):
        """
        validate method Queries the facebook GraphAPI to fetch the user info
        """
        try:
            graph = facebook.GraphAPI(access_token=auth_token)
            profile = graph.request("/me?fields=name,email")
            return profile
        except:
            return None


def register_social_user(request, email: str, name: str, avatar: str = None):
    user = User.objects.get_or_none(email=email)
    if not user:
        name = name.split()
        first_name = name[0]
        last_name = name[1]
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=settings.SOCIAL_SECRET,
            avatar=avatar or settings.DEFAULT_AVATAR_URL,
        )
        EmailUtil.send_welcome_email(request, user)
    return user
