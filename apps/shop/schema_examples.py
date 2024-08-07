from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
)
from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from apps.common.schema_examples import (
    PAGINATED_RESPONSE_EXAMPLE,
    RESPONSE_TYPE,
    SUCCESS_RESPONSE_STATUS,
    UUID_EXAMPLE,
    non_existent_response_example,
    page_parameter_example,
)

CATEGORY_EXAMPLE = {
    "name": "Real Category",
    "slug": "real-category",
    "image": "https://img.com/category/real-category",
}

USER_EXAMPLE = {
    "name": "Real Person",
    "avatar": "https://img.com/avatar/real-person",
}

PRODUCT_EXAMPLE = {
    "seller": USER_EXAMPLE,
    "name": "Real Product",
    "slug": "real-product",
    "desc": "This is a good product. Buy am na",
    "price_old": "25000.00",
    "price_current": "15000.00",
    "category": CATEGORY_EXAMPLE,
    "sizes": ["XS", "S", "M", "L", "XL"],
    "colors": ["Green", "Blue", "Black"],
    "reviews_count": 20,
    "avg_rating": 3.5,
    "image1": "https://img.com/product/image1",
    "image2": "https://img.com/product/image2",
    "image3": "https://img.com/product/image3",
}
PRODUCTS_RESPONSE = {
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
}


CATEGORIES_RESPONSE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Categories Fetched",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Categories Fetched Successfully",
                    "data": [CATEGORY_EXAMPLE],
                },
            )
        ],
    )
}

REVIEW_EXAMPLE = {
    "user": USER_EXAMPLE,
    "rating": 5,
    "text": "This product is one of a king. I highly recommend you buy it",
}

PRODUCT_NON_EXISTENT_RESPONSE = non_existent_response_example("Product")

PRODUCT_RESPONSE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Product Details Fetched",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Product Details Fetched Successfully",
                    "data": PRODUCT_EXAMPLE
                    | {
                        "related_products": [PRODUCT_EXAMPLE],
                        "reviews": PAGINATED_RESPONSE_EXAMPLE
                        | {"items": [REVIEW_EXAMPLE]},
                    },
                },
            )
        ],
    ),
    404: PRODUCT_NON_EXISTENT_RESPONSE,
    401: UNAUTHORIZED_USER_RESPONSE,
}

REVIEW_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Review created",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Review Created Successfully",
                    "data": REVIEW_EXAMPLE,
                },
            )
        ],
    ),
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Review updated",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Review Updated Successfully",
                    "data": REVIEW_EXAMPLE,
                },
            )
        ],
    ),
    404: PRODUCT_NON_EXISTENT_RESPONSE,
    401: UNAUTHORIZED_USER_RESPONSE,
}


PRODUCTS_PARAM_EXAMPLE = [
    OpenApiParameter(
        name="name",
        description="Filter products by its name",
        required=False,
        type=OpenApiTypes.STR,
    ),
    OpenApiParameter(
        name="size",
        type=OpenApiTypes.STR,
        description="Filter products by size. Can be specified multiple times to include multiple sizes.",
        required=False,
        explode=True,
    ),
    OpenApiParameter(
        name="color",
        type=OpenApiTypes.STR,
        description="Filter products by color. Can be specified multiple times to include multiple colors.",
        required=False,
        explode=True,
    ),
    *page_parameter_example("products", 100),
]

WISHLIST_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Product Added To Wishlist. guest_id will only show if you're a guest",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Product Added To Wishlist Successfully",
                    "guest_id": UUID_EXAMPLE,  # Optional
                },
            )
        ],
    ),
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Product Removed From Wishlist. guest_id will only show if you're a guest",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Product Removed From Wishlist Successfully",
                    "guest_id": UUID_EXAMPLE,  # Optional
                },
            )
        ],
    ),
    404: PRODUCT_NON_EXISTENT_RESPONSE,
    401: UNAUTHORIZED_USER_RESPONSE,
}

CATEGORY_NON_EXISTENT_RESPONSE = non_existent_response_example("Category")

PRODUCTS_BY_CATEGORY_RESPONSE_EXAMPLE = PRODUCTS_RESPONSE | {
    404: CATEGORY_NON_EXISTENT_RESPONSE,
    401: UNAUTHORIZED_USER_RESPONSE,
}
