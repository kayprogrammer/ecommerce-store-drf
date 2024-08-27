from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
)

from apps.common.schema_examples import (
    RESPONSE_TYPE,
    SUCCESS_RESPONSE_STATUS,
    UNPROCESSABLE_ENTITY_EXAMPLE,
)

PROFILE_EXAMPLE = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@example.com",
    "avatar_url": "https://johndoeavatar.com",
    "account_type": "BUYER",
}

PROFILE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Profile Fetched Successful",
        examples=[
            OpenApiExample(
                name="Profile Fetched Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "User Profile Fetched",
                    "data": PROFILE_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}

PROFILE_UPDATE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Profile Updated Successful",
        examples=[
            OpenApiExample(
                name="Profile Updated Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "User Updated Fetched",
                    "data": PROFILE_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    422: UNPROCESSABLE_ENTITY_EXAMPLE,
}

ACCOUNT_DEACTIVATION_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="User Account Deactivated",
        examples=[
            OpenApiExample(
                name="Success response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "User Account Deactivated",
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}
