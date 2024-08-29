from apps.common.exceptions import ErrorCode
from apps.common.schema_examples import (
    DATETIME_EXAMPLE,
    ERR_RESPONSE_STATUS,
    RESPONSE_TYPE,
    SUCCESS_RESPONSE_STATUS,
    UNPROCESSABLE_ENTITY_EXAMPLE,
    generate_field_properties_for_swagger,
)
from drf_spectacular.utils import OpenApiResponse, OpenApiExample

from apps.sellers.serializers import SellerApplicationSerializer

UNAUTHORIZED_BUYER_RESPONSE = OpenApiResponse(
    response=RESPONSE_TYPE,
    description="Unauthorized User or Invalid Access Token or Invalid User",
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
        OpenApiExample(
            name="Invalid User",
            value={
                "status": ERR_RESPONSE_STATUS,
                "code": ErrorCode.BUYERS_ONLY,
                "message": "This action is for buyers only!",
            },
        ),
    ],
)

UNAUTHORIZED_SELLER_RESPONSE = OpenApiResponse(
    response=RESPONSE_TYPE,
    description="Unauthorized User or Invalid Access Token or Invalid User",
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
        OpenApiExample(
            name="Invalid User",
            value={
                "status": ERR_RESPONSE_STATUS,
                "code": ErrorCode.SELLERS_ONLY,
                "message": "This action is for sellers only!",
            },
        ),
    ],
)

SELLER_APPLICATION_DATA_EXAMPLE = {
    "full_name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-09-12",
    "business_name": "Jane's Clothings",
    "business_type": "sole_proprietorship",
    "business_registration_number": "123456789",
    "tax_identification_number": "TIN123456789",
    "website_url": "http://www.janesboutique.com",
    "business_description": "We sell fashion accessories and clothing.",
    "business_address": "123 Main St",
    "city": "New York",
    "state_province": "NY",
    "postal_code": "10001",
    "country": "USA",
    "bank_name": "Example Bank",
    "bank_account_number": "987654321",
    "bank_routing_number": "111000025",
    "account_holder_name": "Jane Doe",
    "government_id": "https://file.com/government_id",
    "proof_of_address": "https://file.com/proof_of_address",
    "business_license": "https://file.com/business_license",
    "product_categories": ["Clothing"],
    "expected_sales_volume": "5000-10000 USD",
    "preferred_shipping_method": "standard",
    "additional_comments": "Whatever this is",
    "agree_to_terms": True,
}

SELLER_APPLICATION_RESPONSE_DATA_EXAMPLE = SELLER_APPLICATION_DATA_EXAMPLE | {
    "is_approved": False,
    "application_date": DATETIME_EXAMPLE,
}


properties, required_fields = generate_field_properties_for_swagger(
    SellerApplicationSerializer(), SELLER_APPLICATION_DATA_EXAMPLE
)
SELLER_APPLICATION_REQUEST_EXAMPLE = {
    "multipart/form-data": {
        "type": "object",
        "properties": properties,
        "required": required_fields,
    }
}

SELLER_APPLICATION_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Application sent.",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Application sent Successfully",
                    "data": SELLER_APPLICATION_RESPONSE_DATA_EXAMPLE,
                },
            )
        ],
    ),
    401: UNAUTHORIZED_BUYER_RESPONSE,
    422: UNPROCESSABLE_ENTITY_EXAMPLE,
}
