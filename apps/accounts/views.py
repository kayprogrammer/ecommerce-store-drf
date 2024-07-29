from adrf.views import APIView
from django.conf import settings

from apps.accounts.auth import Authentication, Facebook, Google, register_social_user
from apps.common.exceptions import ErrorCode
from apps.common.responses import CustomResponse


class GoogleAuthView(APIView):
    async def get(self, request, *args, **kwargs):
        user_data = Google.validate(kwargs["token"])
        try:
            user_data["sub"]
        except:
            # Invalid auth token
            return CustomResponse.error(
                message="Invalid Auth Token",
                err_code=ErrorCode.INVALID_TOKEN,
                status_code=401,
            )
        if user_data["aud"] != settings.GOOGLE_CLIENT_ID:
            # Invalid client id
            return CustomResponse.error(
                message="Invalid Client ID",
                err_code=ErrorCode.INVALID_CLIENT_ID,
                status_code=401,
            )
        user = await register_social_user(
            user_data["email"], user_data["name"], user_data["picture"]
        )

        # Generate access and refresh tokens
        access = Authentication.create_access_token(user.id)
        refresh = Authentication.create_refresh_token()
        user.access = access
        user.refresh = refresh
        await user.asave()
        return CustomResponse.success(
            message="Tokens Generation successful",
            data={"access": access, "refresh": refresh},
            status_code=201,
        )


class FacebookAuthView(APIView):
    async def get(self, request, *args, **kwargs):
        user_data = Facebook.validate(kwargs["token"])
        user = await register_social_user(user_data["email"], user_data["name"])

        # Generate access and refresh tokens
        access = Authentication.create_access_token(user.id)
        refresh = Authentication.create_refresh_token()
        user.access = access
        user.refresh = refresh
        await user.asave()
        return CustomResponse.success(
            message="Tokens Generation successful",
            data={"access": access, "refresh": refresh},
            status_code=201,
        )
