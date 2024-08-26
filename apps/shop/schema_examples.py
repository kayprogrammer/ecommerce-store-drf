from drf_spectacular.utils import (
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
)
from apps.accounts.schema_examples import UNAUTHORIZED_USER_RESPONSE
from apps.common.exceptions import ErrorCode
from apps.common.schema_examples import (
    DATETIME_EXAMPLE,
    ERR_RESPONSE_STATUS,
    PAGINATED_RESPONSE_EXAMPLE,
    RESPONSE_TYPE,
    SUCCESS_RESPONSE_STATUS,
    UNPROCESSABLE_ENTITY_EXAMPLE,
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

ORDERITEM_DATA_EXAMPLE = {
    "product": {
        "seller": USER_EXAMPLE,
        "name": "Whatever product",
        "slug": "whatever-product",
        "price": "10000.50",
    },
    "quantity": 5,
    "size": "L",
    "color": "Black",
    "total": 3,
}

CART_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Cart Returned",
        examples=[
            OpenApiExample(
                name="Success Response",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Cart Items Returned",
                    "data": PAGINATED_RESPONSE_EXAMPLE
                    | {"items": ORDERITEM_DATA_EXAMPLE},
                },
            )
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}

ORDERITEM_RESPONSE_EXAMPLE = {
    201: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Item Added",
        examples=[
            OpenApiExample(
                name="Item Added",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Item Added To Cart",
                    "data": ORDERITEM_DATA_EXAMPLE,
                },
            ),
        ],
    ),
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Item Updated/Removed",
        examples=[
            OpenApiExample(
                name="Item Updated",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Item Updated In Cart",
                    "data": ORDERITEM_DATA_EXAMPLE,
                },
            ),
            OpenApiExample(
                name="Item Removed",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Item Removed From Cart",
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
}

SHIPPING_DETAILS_EXAMPLE = {
    "full_name": "John Doe",
    "email": "johndoe@example.com",
    "phone": "+2341099333443",
    "address": "234, My Street, Aboru",
    "city": "Lagos",
    "state": "Lagos",
    "country": "Nigeria",
    "zipcode": "123456",
}

FULL_SHIPPING_DETAILS_EXAMPLE = {"id": UUID_EXAMPLE} | SHIPPING_DETAILS_EXAMPLE

ORDER_DATA_EXAMPLE = {
    "tx_ref": "JSDJASFHSDFHG",
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@email.com",
    "delivery_status": "PENDING",
    "payment_status": "PENDING",
    "payment_method": "PAYSTACK",
    "coupon": "SADJSDJJS",
    "date_delivered": DATETIME_EXAMPLE,
    "shipping_details": SHIPPING_DETAILS_EXAMPLE,
    "subtotal": "10000.00",
    "shipping_fee": "10.00",
    "total": "10010.00",
}

CHECKOUT_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Checkout Successful",
        examples=[
            OpenApiExample(
                name="Checkout Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Checkout Successful",
                    "data": ORDER_DATA_EXAMPLE,
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    404: OpenApiResponse(
        response=RESPONSE_TYPE,
        description=f"Empty Cart",
        examples=[
            OpenApiExample(
                name="Non-existent Response",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "code": ErrorCode.NON_EXISTENT,
                    "message": "No Items in Cart",
                },
            )
        ],
    ),
    422: OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Field errors",
        examples=[
            OpenApiExample(
                name="Invalid/Expired Coupon",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "code": ErrorCode.INVALID_ENTRY,
                    "message": "Invalid Entry",
                    "data": {
                        "coupon": "Coupon is Invalid/Expired!",
                    },
                },
            ),
            OpenApiExample(
                name="Coupon already used",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "code": ErrorCode.INVALID_ENTRY,
                    "message": "Invalid Entry",
                    "data": {
                        "coupon": "You've used this coupon already",
                    },
                },
            ),
            OpenApiExample(
                name="Invalid Shipping ID",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "code": ErrorCode.INVALID_ENTRY,
                    "message": "Invalid Entry",
                    "data": {
                        "shipping_id": "No shipping address with that ID",
                    },
                },
            ),
            OpenApiExample(
                name="Invalid Country",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "code": ErrorCode.INVALID_ENTRY,
                    "message": "Invalid Entry",
                    "data": {
                        "country": "Country does not exist!",
                    },
                },
            ),
        ],
    ),
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
