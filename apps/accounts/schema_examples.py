from drf_spectacular.utils import OpenApiResponse, OpenApiExample
from apps.common.exceptions import ErrorCode
from apps.common.schema_examples import (
    ERR_RESPONSE_STATUS,
    RESPONSE_TYPE,
    SUCCESS_RESPONSE_STATUS,
)

TOKEN_EXAMPLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

AUTH_RESPONSE = {
    201: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Tokens Generated.",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Tokens Generation successful",
                    "data": {
                        "access": TOKEN_EXAMPLE,
                        "refresh": TOKEN_EXAMPLE,
                    },
                },
            )
        ],
    ),
    401: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Invalid Auth Token or Invalid Client ID",
        examples=[
            OpenApiExample(
                name="Invalid Auth Token",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "code": ErrorCode.INVALID_TOKEN,
                    "message": "Invalid Auth Token",
                },
            ),
            OpenApiExample(
                name="Invalid Client ID",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "code": ErrorCode.INVALID_CLIENT_ID,
                    "message": "Invalid Client ID",
                },
            ),
        ],
    ),
}


AUTH_REFRESH_RESPONSE = {
    201: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Tokens Generated.",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Tokens Refresh successful",
                    "data": {
                        "access": TOKEN_EXAMPLE,
                        "refresh": TOKEN_EXAMPLE,
                    },
                },
            )
        ],
    ),
    401: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Invalid Refresh Token",
        examples=[
            OpenApiExample(
                name="Invalid Refresh Token",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "code": ErrorCode.INVALID_TOKEN,
                    "message": "Refresh token is invalid or expired",
                },
            ),
        ],
    ),
}

UNAUTHORIZED_USER_RESPONSE = OpenApiResponse(
    response=RESPONSE_TYPE,
    description="Unauthorized User or Invalid Access Token",
    examples=[
        OpenApiExample(
            name="Unauthorized User",
            value={
                "status": ERR_RESPONSE_STATUS,
                "code": ErrorCode.INVALID_AUTH,
                "message": "Auth Bearer not provided!",
            },
        ),
        OpenApiExample(
            name="Invalid Access Token",
            value={
                "status": ERR_RESPONSE_STATUS,
                "code": ErrorCode.INVALID_TOKEN,
                "message": "Access Token is Invalid or Expired!",
            },
        ),
    ],
)

AUTH_LOGOUT_RESPONSE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Logout Successful.",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Logout Successful",
                },
            )
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}
