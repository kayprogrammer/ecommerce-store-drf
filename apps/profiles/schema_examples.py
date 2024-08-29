from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
)

from apps.common.schema_examples import (
    PAGINATED_RESPONSE_EXAMPLE,
    RESPONSE_TYPE,
    SUCCESS_RESPONSE_STATUS,
    UNPROCESSABLE_ENTITY_EXAMPLE,
    non_existent_response_example,
    page_parameter_example,
)
from apps.shop.schema_examples import FULL_SHIPPING_DETAILS_EXAMPLE, ORDER_DATA_EXAMPLE

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

SHIPPING_ADDRESSES_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Shipping addresses returned",
        examples=[
            OpenApiExample(
                name="Shipping addresses returned",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Shipping addresses returned",
                    "data": [FULL_SHIPPING_DETAILS_EXAMPLE],
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}

SHIPPING_ADDRESS_CREATE_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Shipping address created successfully",
        examples=[
            OpenApiExample(
                name="Shipping address created successfully",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Shipping address created successfully",
                    "data": FULL_SHIPPING_DETAILS_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    422: UNPROCESSABLE_ENTITY_EXAMPLE,
}

SHIPPING_ADDRESS_GET_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Shipping address fetched successfully",
        examples=[
            OpenApiExample(
                name="Shipping address fetched successfully",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Shipping address fetched successfully",
                    "data": FULL_SHIPPING_DETAILS_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    404: non_existent_response_example("Shipping Address"),
}

SHIPPING_ADDRESS_UPDATE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Shipping address updated successfully",
        examples=[
            OpenApiExample(
                name="Shipping address updated successfully",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Shipping address updated successfully",
                    "data": FULL_SHIPPING_DETAILS_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    404: non_existent_response_example("Shipping Address"),
    422: UNPROCESSABLE_ENTITY_EXAMPLE,
}

SHIPPING_ADDRESS_DELETE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Deletion Successful.",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Shipping address deleted successfully",
                },
            )
        ],
    ),
    404: non_existent_response_example("Shipping Address"),
    401: UNAUTHORIZED_USER_RESPONSE,
}

ORDERS_PARAM_EXAMPLE = [
    OpenApiParameter(
        name="payment_status",
        description="Filter products by payment status",
        required=False,
        type=OpenApiTypes.STR,
    ),
    OpenApiParameter(
        name="delivery_status",
        description="Filter products by delivery status",
        required=False,
        type=OpenApiTypes.STR,
    ),
    *page_parameter_example("orders", 100),
]

ORDERS_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Orders Fetched",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Orders Fetched Successfully",
                    "data": PAGINATED_RESPONSE_EXAMPLE
                    | {"orders": [ORDER_DATA_EXAMPLE]},
                },
            )
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}
