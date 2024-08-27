from adrf.views import APIView
from drf_spectacular.utils import extend_schema
from apps.common.permissions import IsAuthenticatedCustom, set_dict_attr
from apps.common.responses import CustomResponse
from apps.profiles.schema_examples import (
    ACCOUNT_DEACTIVATION_RESPONSE_EXAMPLE,
    PROFILE_RESPONSE_EXAMPLE,
    PROFILE_UPDATE_RESPONSE_EXAMPLE,
)
from apps.profiles.serializers import ProfileSerializer

tags = ["Profiles"]


class ProfileView(APIView):
    """
    A asynchronous view to handle the retrieval and updating of user profiles.

    Attributes:
        serializer_class (ProfileSerializer): The serializer class used to validate and serialize profile data.
        permission_classes (tuple): Permissions required to access this view, in this case, custom authentication.

    Methods:
        get(request):
            Retrieves the profile of the authenticated user.

        put(request):
            Updates the profile of the authenticated user.
    """

    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedCustom,)

    @extend_schema(
        summary="Retrieve Profile",
        description="""
            This endpoint allows a user to retrieve his/her profile.
        """,
        tags=tags,
        responses=PROFILE_RESPONSE_EXAMPLE,
    )
    async def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return CustomResponse.success(
            message="User Profile Fetched", data=serializer.data
        )

    @extend_schema(
        summary="Update Profile",
        description="""
            This endpoint allows a user to update his/her profile.
        """,
        tags=tags,
        request={"multipart/form-data": serializer_class},
        responses=PROFILE_UPDATE_RESPONSE_EXAMPLE,
    )
    async def put(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = set_dict_attr(user, serializer.validated_data)
        await user.asave()
        serializer = self.serializer_class(user)
        return CustomResponse.success(
            message="User Profile Updated", data=serializer.data
        )

    @extend_schema(
        summary="Deactivate account",
        description="""
            This endpoint allows a user to deactivate his/her account.
        """,
        tags=tags,
        responses=ACCOUNT_DEACTIVATION_RESPONSE_EXAMPLE,
    )
    async def delete(self, request):
        user = request.user
        user.is_active = False
        await user.asave()
        return CustomResponse.success(message="User Account Deactivated")
