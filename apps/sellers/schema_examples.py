from apps.accounts.schema_examples import (
    UNAUTHORIZED_BUYER_RESPONSE,
    UNAUTHORIZED_USER_RESPONSE,
)
from apps.common.exceptions import ErrorCode
from apps.common.schema_examples import (
    DATETIME_EXAMPLE,
    ERR_RESPONSE_STATUS,
    PAGINATED_RESPONSE_EXAMPLE,
    RESPONSE_TYPE,
    SUCCESS_RESPONSE_STATUS,
    UNPROCESSABLE_ENTITY_EXAMPLE,
    generate_field_properties_for_swagger,
    non_existent_response_example,
)
from drf_spectacular.utils import OpenApiResponse, OpenApiExample

from apps.sellers.serializers import ProductCreateSerializer, SellerSerializer
from apps.shop.schema_examples import PRODUCT_EXAMPLE

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
    "country": "United States",
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
    "slug": "jones-clothing",
    "is_approved": False,
    "application_date": DATETIME_EXAMPLE,
}


properties = generate_field_properties_for_swagger(
    SellerSerializer(), SELLER_APPLICATION_DATA_EXAMPLE
)
SELLER_APPLICATION_REQUEST_EXAMPLE = {
    "multipart/form-data": {
        "type": "object",
        "properties": properties,
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

SELLER_PRODUCTS_RESPONSE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Products Fetched. guest_id will only show for guest users",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Products Fetched Successfully",
                    "data": PAGINATED_RESPONSE_EXAMPLE
                    | {"products": [PRODUCT_EXAMPLE]},
                },
            )
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    404: non_existent_response_example("Seller"),
}

PRODUCT_CREATE_EXAMPLE = {
    "name": "Black Trousers for men",
    "desc": "This is a product you must buy by force",
    "price_current": "10000.00",
    "category_slug": "clothing",
    "sizes": ["S", "M"],
    "colors": ["Black", "White"],
    "in_stock": 50,
    "image1": "https://good-looking-image.com",
    "image2": "https://good-looking-image.com",
    "image3": "https://good-looking-image.com",
}

properties = generate_field_properties_for_swagger(
    ProductCreateSerializer(), PRODUCT_CREATE_EXAMPLE
)
PRODUCT_CREATE_REQUEST_EXAMPLE = {
    "multipart/form-data": {
        "type": "object",
        "properties": properties,
    }
}

PRODUCT_CREATE_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Product created.",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Product created successfully",
                    "data": PRODUCT_EXAMPLE,
                },
            )
        ],
    ),
    401: UNAUTHORIZED_SELLER_RESPONSE,
    422: UNPROCESSABLE_ENTITY_EXAMPLE,
}
