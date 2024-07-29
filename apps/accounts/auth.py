from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from datetime import datetime, timedelta, UTC
import jwt, random, string, facebook

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


async def register_social_user(email: str, name: str, avatar: str = None):
    user = await User.objects.aget_or_none(email=email)
    if not user:
        name = name.split()
        first_name = name[0]
        last_name = name[1]
        user = await User.objects.acreate_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=settings.SOCIAL_SECRET,
            avatar=avatar or settings.DEFAULT_AVATAR_URL,
        )
        EmailUtil.send_welcome_email(user)
    return user


ALGORITHM = "HS256"


class Authentication:
    # generate random string
    def get_random(length: int):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    # generate access token based and encode user's id
    def create_access_token(user_id: str):
        expire = datetime.now(UTC) + timedelta(
            minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode = {"exp": expire, "user_id": user_id}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    # generate random refresh token
    def create_refresh_token():
        expire = datetime.now(UTC) + timedelta(
            minutes=int(settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )
        return jwt.encode(
            {"exp": expire, "data": Authentication.get_random(10)},
            settings.SECRET_KEY,
            algorithm=ALGORITHM,
        )

    # deocde access token from header
    def decode_jwt(token: str):
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        except:
            decoded = False
        return decoded

    def decodeAuthorization(token: str):
        token = token[7:]
        decoded = Authentication.decode_jwt(token)
        if not decoded:
            return None
        user = User.objects.get_or_none(id=decoded["user_id"], access=token)
        return user
