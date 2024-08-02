from adrf.views import APIView
from drf_spectacular.utils import extend_schema

from .auth import Authentication, Facebook, Google, register_social_user
from .models import User
from .schema_examples import (
    AUTH_LOGOUT_RESPONSE,
    AUTH_REFRESH_RESPONSE,
    AUTH_RESPONSE,
)
from .serializers import TokenSerializer
from apps.common.exceptions import ErrorCode, RequestError
from apps.common.permissions import IsAuthenticatedCustom
from apps.common.responses import CustomResponse

tags = ["Auth"]


class GoogleAuthView(APIView):
    """
    Handles Google authentication and token generation.

    Attributes:
        serializer_class (TokenSerializer): The serializer used to validate and process the request data.

    Methods:
        post(request, *args, **kwargs):
            Validates the provided Google auth token, registers the user if necessary, and generates access and refresh tokens.
    """

    serializer_class = TokenSerializer

    @extend_schema(
        summary="Google Auth",
        description="""
            This endpoint generates token for authentication and authorization.
            When you click on the Try It Out button, there will be a button for you to generate a google auth token.
            This is to help you test the API without having to create your own facebook frontend/client to test with.
        """,
        tags=tags,
        responses=AUTH_RESPONSE,
    )
    async def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data, err_code, err_msg = Google.validate(
            serializer.validated_data["token"]
        )
        if err_code:
            return CustomResponse.error(
                message=err_msg,
                err_code=err_code,
                status_code=401,
            )
        user = await register_social_user(
            user_data["email"], user_data["name"], user_data["picture"]
        )

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
    """
    Handles Facebook authentication and token generation.

    Attributes:
        serializer_class (TokenSerializer): The serializer used to validate and process the request data.

    Methods:
        post(request, *args, **kwargs):
            Validates the provided Facebook auth token, registers the user if necessary, and generates access and refresh tokens.
    """

    serializer_class = TokenSerializer

    @extend_schema(
        summary="Facebook Auth",
        description="""
            This endpoint generates token for authentication and authorization.
            When you click on the Try It Out button, there will be a button for you to generate a facebook auth token.
            This is to help you test the API without having to create your own google frontend/client to test with.
        """,
        tags=tags,
        responses=AUTH_RESPONSE,
    )
    async def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data, err_code, err_msg = Facebook.validate(
            serializer.validated_data["token"]
        )
        if err_code:
            return CustomResponse.error(
                message=err_msg,
                err_code=err_code,
                status_code=401,
            )

        user = await register_social_user(user_data["email"], user_data["name"])

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


class RefreshTokensView(APIView):
    """
    Handles token refresh to generate new access and refresh tokens.

    Attributes:
        serializer_class (TokenSerializer): The serializer used to validate the refresh token.

    Methods:
        post(request):
            Validates the refresh token and generates new access and refresh tokens if valid.
    """

    serializer_class = TokenSerializer

    @extend_schema(
        summary="Refresh tokens",
        description="""
            This endpoint refresh tokens by generating new access and refresh tokens for a user
        """,
        responses=AUTH_REFRESH_RESPONSE,
        tags=tags,
    )
    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        user = await User.objects.aget_or_none(refresh=token)
        if not user or not Authentication.decode_jwt(token):
            raise RequestError(
                err_code=ErrorCode.INVALID_TOKEN,
                err_msg="Refresh token is invalid or expired",
                status_code=401,
            )

        user.access = Authentication.create_access_token(user.id)
        user.refresh = Authentication.create_refresh_token()
        await user.asave()

        return CustomResponse.success(
            message="Tokens refresh successful",
            data={"access": user.access, "refresh": user.refresh},
            status_code=201,
        )


class LogoutView(APIView):
    """
    Handles user logout by invalidating access and refresh tokens.

    Methods:
        get(request):
            Logs the user out by setting the access and refresh tokens to None.
    """

    permission_classes = (IsAuthenticatedCustom,)

    @extend_schema(
        summary="Logout User",
        description="""
            This endpoint logs a user out by invalidating our access and refresh tokens
        """,
        responses=AUTH_LOGOUT_RESPONSE,
        tags=tags,
    )
    async def get(self, request):
        user = request.user
        user.access = user.refresh = None
        await user.asave()
        return CustomResponse.success(
            message="Logout Successful",
        )
