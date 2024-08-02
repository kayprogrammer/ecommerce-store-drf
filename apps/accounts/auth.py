from uuid import UUID
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from datetime import datetime, timedelta, UTC
import jwt, random, string, facebook

from apps.common.exceptions import ErrorCode

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
            if not "sub" in idinfo.keys():
                return None, ErrorCode.INVALID_TOKEN, "Invalid Auth Token"
            if idinfo["aud"] != settings.GOOGLE_CLIENT_ID:
                return None, ErrorCode.INVALID_CLIENT_ID, "Invalid Client ID"
            return idinfo, None, None
        except:
            return None, ErrorCode.INVALID_TOKEN, "Invalid Auth Token"


class Facebook:
    """
    Facebook class to fetch the user info and return it
    """

    @staticmethod
    def validate(auth_token):
        """
        validate method Queries the facebook GraphAPI to fetch the user info
        """
        graph = facebook.GraphAPI(access_token=auth_token)
        try:
            app = graph.request(f"/app")
            if app["id"] != settings.FACEBOOK_APP_ID:
                return None, ErrorCode.INVALID_CLIENT_ID, "Invalid Client ID"
        except facebook.GraphAPIError:
            return None, ErrorCode.INVALID_TOKEN, "Invalid Auth Token"
        profile = graph.request("/me?fields=name,email")
        return profile, None, None


async def register_social_user(
    email: str, name: str, avatar: str = settings.DEFAULT_AVATAR_URL
):
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
            social_avatar=avatar,
        )
        EmailUtil.send_welcome_email(user)
    return user


ALGORITHM = "HS256"


class Authentication:
    # generate random string
    def get_random(length: int):
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    # generate access token based and encode user's id
    def create_access_token(user_id: UUID):
        expire = datetime.now(UTC) + timedelta(
            minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode = {"exp": expire, "user_id": str(user_id)}
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
