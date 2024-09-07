from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from adrf.views import APIView
from drf_spectacular.utils import extend_schema
from apps.accounts.senders import EmailUtil
from apps.common.decorators import aatomic
from apps.common.exceptions import (
    ErrorCode,
    NotFoundError,
    RequestError,
    ValidationErr,
)
from apps.common.paginators import CustomPagination
from apps.common.permissions import (
    IsAuthenticatedCustom,
    IsAuthenticatedOrGuestCustom,
)
from apps.common.responses import CustomResponse
from apps.common.schema_examples import page_parameter_example
from apps.common.utils import (
    REVIEWS_AND_RATING_WISHLISTED_CARTED_ANNOTATION,
    get_user_or_guest,
)
from apps.shop.models import (
    Category,
    Country,
    Coupon,
    Order,
    OrderItem,
    Product,
    Review,
    ShippingAddress,
    Wishlist,
)
from apps.shop.schema_examples import (
    CART_RESPONSE_EXAMPLE,
    CATEGORIES_RESPONSE,
    CHECKOUT_RESPONSE_EXAMPLE,
    ORDERITEM_RESPONSE_EXAMPLE,
    PRODUCT_RESPONSE,
    PRODUCTS_BY_CATEGORY_RESPONSE_EXAMPLE,
    PRODUCTS_PARAM_EXAMPLE,
    PRODUCTS_RESPONSE,
    REVIEW_RESPONSE_EXAMPLE,
    WISHLIST_RESPONSE_EXAMPLE,
)
from apps.shop.serializers import (
    CategorySerializer,
    CheckoutSerializer,
    OrderItemSerializer,
    OrderItemsResponseDataSerializer,
    OrderSerializer,
    ProductDetailSerializer,
    ProductsResponseDataSerializer,
    ReviewSerializer,
    ToggleCartItemSerializer,
)
from apps.shop.utils import (
    append_shipping_details,
    fetch_products,
    update_product_in_stock,
    verify_webhook_signature,
)
from asgiref.sync import sync_to_async
import hashlib, hmac, json, decimal

tags = ["Shop"]


class CategoriesView(APIView):
    """
    API view to fetch all categories.

    Methods:
        get: Asynchronously fetches and returns all categories.
    """

    serializer_class = CategorySerializer

    @extend_schema(
        summary="Categories Fetch",
        description="""
            This endpoint returns all categories.
        """,
        tags=tags,
        responses=CATEGORIES_RESPONSE,
    )
    async def get(self, request, *args, **kwargs):
        """
        Handle async GET requests to fetch all categories.

        Args:
            request: The request object.

        Returns:
            CustomResponse: A response containing serialized category data.
        """
        categories = await sync_to_async(list)(Category.objects.all())
        serializer = self.serializer_class(categories, many=True)
        return CustomResponse.success(
            message="Categories fetched successfully", data=serializer.data
        )


class ProductsView(APIView):
    """
    API view to fetch all products.

    Methods:
        get: Asynchronously fetches and returns all products, with optional filtering by name, size, or color.
    """

    permission_classes = [IsAuthenticatedOrGuestCustom]
    serializer_class = ProductsResponseDataSerializer
    paginator_class = CustomPagination()

    @extend_schema(
        summary="Products Fetch",
        description="""
            This endpoint returns all products.
            Products can be filtered by name, sizes or colors.
        """,
        tags=tags,
        responses=PRODUCTS_RESPONSE,
        parameters=PRODUCTS_PARAM_EXAMPLE,
    )
    async def get(self, request, *args, **kwargs):
        """
        Handle async GET requests to fetch all products, with optional filtering.

        Args:
            request: The request object.

        Returns:
            CustomResponse: A response containing serialized and paginated product data.
        """
        user, guest = get_user_or_guest(request.user)
        products = await fetch_products(request, user, guest)

        paginated_data = self.paginator_class.paginate_queryset(products, request)
        serializer = self.serializer_class(paginated_data)
        return CustomResponse.success(
            message="Products Fetched Successfully", data=serializer.data
        )


class ProductView(APIView):
    """
    API view to fetch details of a specific product and handle reviews.

    Methods:
        get: Asynchronously fetches and returns product details by slug.
        post: Asynchronously allows a user to write or update a review for a product.
        get_permissions: Returns custom permissions for POST requests.
    """

    permission_classes = [IsAuthenticatedOrGuestCustom]
    serializer_class = ProductDetailSerializer
    review_serializer_class = ReviewSerializer
    paginator_class = CustomPagination()

    @extend_schema(
        summary="Product Details Fetch",
        description="""
            This endpoint returns the details for a product via the slug.
        """,
        tags=tags,
        parameters=page_parameter_example("reviews", 100),
        responses=PRODUCT_RESPONSE,
    )
    async def get(self, request, *args, **kwargs):
        """
        Handle async GET requests to fetch product details by slug.

        Args:
            request: The request object.
            kwargs: Contains the product slug.

        Returns:
            CustomResponse: A response containing serialized product details.
        """
        user, guest = get_user_or_guest(request.user)
        product = await (
            Product.objects.select_related("category", "seller", "seller__user")
            .prefetch_related("sizes", "colors", "reviews", "reviews__user")
            .annotate(**REVIEWS_AND_RATING_WISHLISTED_CARTED_ANNOTATION(user, guest))
            .aget_or_none(in_stock__gt=0, slug=kwargs["slug"])
        )
        if not product:
            raise RequestError(
                err_msg="Product does not exist!",
                err_code=ErrorCode.NON_EXISTENT,
                status_code=404,
            )

        product_reviews = await sync_to_async(list)(
            product.reviews.select_related("user").order_by("-rating")
        )
        paginated_data = self.paginator_class.paginate_queryset(
            product_reviews, request
        )
        product.related_products = await sync_to_async(list)(
            Product.objects.select_related("category", "seller")
            .prefetch_related("sizes", "colors")
            .annotate(**REVIEWS_AND_RATING_WISHLISTED_CARTED_ANNOTATION(user, guest))
            .filter(category_id=product.category_id, in_stock__gt=0)
            .exclude(id=product.id)[:10]
        )
        product.reviews_data = paginated_data
        serializer = self.serializer_class(product)
        return CustomResponse.success(
            message="Product Details Fetched Successfully", data=serializer.data
        )

    @extend_schema(
        summary="Write a review",
        description="""
            This endpoint allows a user to write a review for a particular product.
            If they already have an existing one, then it updates the review instead.
        """,
        tags=tags,
        request=ReviewSerializer,
        responses=REVIEW_RESPONSE_EXAMPLE,
    )
    async def post(self, request, *args, **kwargs):
        """
        Handle async POST requests to write a review for a product.

        Args:
            request: The request object.
            kwargs: Contains the product slug.

        Returns:
            CustomResponse: A response with the status of the review creation or update.
        """
        user = request.user
        serializer = self.review_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = await Product.objects.aget_or_none(slug=kwargs["slug"])
        if not product:
            raise RequestError(
                err_msg="Product does not exist!",
                err_code=ErrorCode.NON_EXISTENT,
                status_code=404,
            )
        data = serializer.validated_data
        review, created = await Review.objects.select_related("user").aupdate_or_create(
            user=user,
            product_id=product.id,
            defaults={"text": data["text"], "rating": data["rating"]},
        )
        status_code = 201
        response_message_substring = "Created"
        if not created:
            status_code = 200
            response_message_substring = "Updated"
        serializer = self.review_serializer_class(review)
        return CustomResponse.success(
            message=f"Review {response_message_substring} successfully",
            data=serializer.data,
            status_code=status_code,
        )

    def get_permissions(self):
        """
        Return custom permissions for POST requests.

        Returns:
            list: List of permission classes for POST method.
        """
        if self.request.method == "POST":
            return [IsAuthenticatedCustom()]
        return [IsAuthenticatedOrGuestCustom()]


class WishlistView(APIView):
    """
    API view to fetch all products in a wishlist.

    Methods:
        get: Asynchronously fetches and returns all products in user's or guest wishlist, with optional filtering by name, size, or color.
    """

    serializer_class = ProductsResponseDataSerializer
    paginator_class = CustomPagination()
    permission_classes = [IsAuthenticatedOrGuestCustom]

    @extend_schema(
        summary="Wishlist Products Fetch",
        description="""
            This endpoint returns all products in the user or guest wishlist.
            Products can be filtered by name, sizes or colors.
        """,
        tags=tags,
        responses=PRODUCTS_RESPONSE,
        parameters=PRODUCTS_PARAM_EXAMPLE,
    )
    async def get(self, request):
        user, guest = get_user_or_guest(request.user)
        products = await fetch_products(
            request, user, guest, {"wishlist__user": user, "wishlist__guest": guest}
        )
        paginated_data = self.paginator_class.paginate_queryset(products, request)
        serializer = self.serializer_class(paginated_data)
        return CustomResponse.success(
            message="Wishlist Products Fetched Successfully", data=serializer.data
        )


class ToggleWishlistView(APIView):
    """
    API view to toggle product to and from wishlist.

    Methods:
        get: Asynchronously adds or remove a product from a user or guest wishlist.
    """

    permission_classes = [IsAuthenticatedOrGuestCustom]

    @extend_schema(
        summary="Toggle Wishlist",
        description="""
            This endpoint allows users or guests to add or remove product from their wishlist. 
            For user, use the jwt bearer auth, and for a guest, use the provided guest_id.
        """,
        tags=tags,
        responses=WISHLIST_RESPONSE_EXAMPLE,
    )
    async def get(self, request, *args, **kwargs):
        user, guest = get_user_or_guest(request.user)
        product = await Product.objects.aget_or_none(slug=kwargs["slug"])
        if not product:
            raise RequestError(
                err_msg="Product does not exist!",
                err_code=ErrorCode.NON_EXISTENT,
                status_code=404,
            )
        wishlist, created = await Wishlist.objects.aget_or_create(
            user=user, guest=guest, product=product
        )
        response_message_substring = "Added To"
        status_code = 201
        if not created:
            status_code = 200
            response_message_substring = "Removed From"
            await wishlist.adelete()
        return CustomResponse.success(
            message=f"Product {response_message_substring} Wishlist Successfully",
            status_code=status_code,
        )


class ProductsByCategoryView(APIView):
    """
    API view to fetch all products in a particular category.

    Methods:
        get: Asynchronously fetches and returns all products in a particular category, with optional filtering by name, size, or color.
    """

    serializer_class = ProductsResponseDataSerializer
    paginator_class = CustomPagination()
    permission_classes = [IsAuthenticatedOrGuestCustom]

    @extend_schema(
        summary="Category Products Fetch",
        description="""
            This endpoint returns all products in a particular category.
        """,
        tags=tags,
        responses=PRODUCTS_BY_CATEGORY_RESPONSE_EXAMPLE,
        parameters=PRODUCTS_PARAM_EXAMPLE,
    )
    async def get(self, request, *args, **kwargs):
        user, guest = get_user_or_guest(request.user)
        category = await Category.objects.aget_or_none(slug=kwargs["slug"])
        if not category:
            raise RequestError(
                err_msg="Category does not exist!",
                err_code=ErrorCode.NON_EXISTENT,
                status_code=404,
            )

        products = await fetch_products(request, user, guest, {"category": category})
        paginated_data = self.paginator_class.paginate_queryset(products, request)
        serializer = self.serializer_class(paginated_data)
        return CustomResponse.success(
            message="Products Fetched Successfully", data=serializer.data
        )


class CartView(APIView):
    """
    API view to fetch all items in a user or guest cart.

    Methods:
        get: Asynchronously fetches and returns all items in a user or guest's cart.
    """

    serializer_class = OrderItemsResponseDataSerializer
    item_serializer_class = OrderItemSerializer
    serializer_create_class = ToggleCartItemSerializer
    paginator_class = CustomPagination()
    permission_classes = [IsAuthenticatedOrGuestCustom]

    @extend_schema(
        summary="Cart Items Fetch",
        description="""
            This endpoint returns all items in a user or guest's cart.
        """,
        tags=tags,
        responses=CART_RESPONSE_EXAMPLE,
        parameters=page_parameter_example("cart_items", 100),
    )
    async def get(self, request, *args, **kwargs):
        user, guest = get_user_or_guest(request.user)
        orderitems = await sync_to_async(list)(
            OrderItem.objects.filter(user=user, guest=guest, order=None).select_related(
                "product", "product__seller", "product__seller__user", "size", "color"
            )
        )
        paginated_data = self.paginator_class.paginate_queryset(orderitems, request)
        serializer = self.serializer_class(paginated_data)
        return CustomResponse.success(
            message="Cart Items Returned", data=serializer.data
        )

    @extend_schema(
        summary="Toggle Item in cart",
        description="""
            This endpoint allows a user or guest to add/update/remove an item in cart.
            If quantity is 0, the item is removed from cart
        """,
        tags=tags,
        request=serializer_create_class,
        responses=ORDERITEM_RESPONSE_EXAMPLE,
    )
    @aatomic
    async def post(self, request, *args, **kwargs):
        user, guest = get_user_or_guest(request.user)
        serializer = self.serializer_create_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        quantity = data["quantity"]
        size = data.get("size")
        color = data.get("color")

        product = await Product.objects.select_related("seller").aget_or_none(
            slug=data["slug"]
        )
        if not product:
            raise ValidationErr("slug", "No Product with that slug")
        if not size and (await product.sizes.aexists()):
            raise ValidationErr("size", "Enter a size")
        if not color and (await product.colors.aexists()):
            raise ValidationErr("color", "Enter a color")

        if size:
            size = await product.sizes.aget_or_none(value=size)
            if not size:
                raise ValidationErr("size", "Invalid size selected")

        if color:
            color = await product.colors.aget_or_none(value=color)
            if not color:
                raise ValidationErr("color", "Invalid color selected")

        orderitem, created = await OrderItem.objects.aupdate_or_create(
            user=user,
            guest=guest,
            order_id=None,
            product=product,
            size=size,
            color=color,
            defaults={"quantity": quantity},
        )
        resp_message_substring = "Updated In"
        status_code = 200
        if created:
            status_code = 201
            resp_message_substring = "Added To"
        if orderitem.quantity == 0:
            resp_message_substring = "Removed From"
            # Delete item from cart
            await orderitem.adelete()
        data = None
        if resp_message_substring != "Removed From":
            orderitem.product = product
            orderitem.size = size
            orderitem.color = color
            serializer = self.item_serializer_class(orderitem)
            data = serializer.data
        return CustomResponse.success(
            message=f"Item {resp_message_substring} Cart",
            data=data,
            status_code=status_code,
        )


class CheckoutView(APIView):
    """
    View for handling the order creation process.

    This view allows authenticated users to create an order and proceed to payment.
    Users can apply coupons, use existing shipping addresses, or create new shipping
    addresses during the checkout process. Supported payment methods include PAYSTACK
    and PAYPAL.

    Attributes:
        serializer_create_class (CheckoutSerializer): Serializer class for creating an order.
        serializer_response_class (OrderSerializer): Serializer class for the response after creating an order.
        permission_classes (list): List of permission classes, allowing only authenticated users.

    Methods:
        post(request, *args, **kwargs): Handles the checkout process and returns a response with the order details.
    """

    serializer_create_class = CheckoutSerializer
    serializer_response_class = OrderSerializer
    permission_classes = [IsAuthenticatedCustom]

    @extend_schema(
        summary="Checkout",
        description="""
            This endpoint allows a user to create an order through which payment can then be made through a frontend sdk..
            Use the tx_ref in the response to make payment to paystack or paypal
            Enter a shipping id to use a created shipping address, otherwise enter shipping for new details entirely
            Payment Methods allowed: "PAYSTACK", "PAYPAL"
            If you select paystack, a paystack button will be generated before the cancel button which represents a test client you can use to test the returned data
        """,
        tags=tags,
        request=serializer_create_class,
        responses=CHECKOUT_RESPONSE_EXAMPLE,
    )
    @aatomic
    async def post(self, request, *args, **kwargs):
        # Proceed to checkout
        user = request.user
        orderitems = OrderItem.objects.filter(user=user, order=None)
        if not await orderitems.aexists():
            raise NotFoundError(err_msg="No Items in Cart")

        serializer = self.serializer_create_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        coupon = data.get("coupon")
        if coupon:
            coupon = await Coupon.objects.aget_or_none(
                code=coupon, expiry_date__gt=timezone.now()
            )
            if not coupon:
                raise ValidationErr("coupon", "Coupon is Invalid/Expired!")
            if await Order.objects.filter(user=user, coupon__code=coupon).aexists():
                raise ValidationErr("coupon", "You've used this coupon already")

        shipping_id = data.get("shipping_id")
        shipping = data.get("shipping")
        if shipping:
            country = await Country.objects.aget_or_none(name=shipping["country"])
            if not country:
                raise ValidationErr("shipping", {"country": "Country does not exist"})
            shipping["country"] = country
            # Get or create shipping based on the shipping details entered by a user
            shipping, _ = await ShippingAddress.objects.select_related(
                "country"
            ).aget_or_create(**shipping, defaults={"user": user})
        if shipping_id:
            # Get shipping details based on the shipping id entered by a user
            shipping = await ShippingAddress.objects.select_related(
                "country"
            ).aget_or_none(id=shipping_id)
            if not shipping:
                raise ValidationErr("shipping_id", "No shipping address with that ID")

        data_to_append_to_order = append_shipping_details(
            {
                "payment_method": data["payment_method"],
            },
            shipping,
        )
        order = await Order.objects.acreate(
            user=user, coupon=coupon, **data_to_append_to_order
        )
        await orderitems.aupdate(order=order)
        # Reload order to prevent async errors
        order = (
            await Order.objects.select_related("user")
            .prefetch_related("orderitems", "orderitems__product")
            .aget_or_none(id=order.id)
        )
        serializer = self.serializer_response_class(order)
        return CustomResponse.success(
            message="Checkout Successful", data=serializer.data
        )


@csrf_exempt
def paystack_webhook(request):
    """
    Handle Paystack webhook events.

    This function processes webhook events sent by Paystack, such as payment success notifications.
    It verifies the event signature, retrieves the relevant order, and updates the order status
    based on the payment outcome.

    Args:
        request (HttpRequest): The HTTP request object containing the webhook payload.

    Returns:
        HttpResponse: An HTTP response indicating the result of the webhook processing.
    """

    # retrive the payload from the request body
    payload = request.body
    # signature header to to verify the request is from paystack
    sig_header = request.headers["x-paystack-signature"]
    body, event = None, None

    try:
        # sign the payload with `HMAC SHA512`
        hash = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
            payload,
            digestmod=hashlib.sha512,
        ).hexdigest()
        # compare our signature with paystacks signature
        if hash == sig_header:
            # if signature matches,
            # proceed to retrive event status from payload
            body_unicode = payload.decode("utf-8")
            body = json.loads(body_unicode)
            # event status
            event = body["event"]
        else:
            raise Exception
    except Exception as e:
        return HttpResponse(status=400)

    if event == "charge.success":
        data = body["data"]
        if (data["status"] == "success") and (data["gateway_response"] == "Successful"):
            order = (
                Order.objects.prefetch_related("orderitems")
                .prefetch_related("orderitems__product")
                .get_or_none(tx_ref=data["reference"])
            )
            amount_paid = data["amount"] / 100
            if not order:
                customer = data["customer"]
                name = f"{customer.get('first_name', 'John')} {customer.get('last_name', 'Doe')}"
                email = customer.get("email")
                EmailUtil.send_payment_failed_email(name, email, amount_paid)
                return HttpResponse(status=200)
            amount_payable = order.get_cart_total
            user = order.user
            if amount_paid < amount_payable:
                # You made an invalid payment
                EmailUtil.send_payment_failed_email(
                    user.full_name, user.email, amount_paid
                )
                order.payment_status = "FAILED"
                order.save()
                return HttpResponse(status=200)

            order.payment_status = "SUCCESSFUL"
            order.save()
            update_product_in_stock(order.orderitems.all())
            # Send email
            EmailUtil.send_payment_success_email(
                user.full_name, user.email, amount_payable
            )
        else:
            return HttpResponse(status=200)
    return HttpResponse(status=200)


@csrf_exempt
def paypal_webhook(request):
    """
    Handle PayPal webhook events.

    This function processes webhook events sent by PayPal, such as payment completion notifications.
    It verifies the event signature, retrieves the relevant order, and updates the order status
    based on the payment outcome.

    Args:
        request (HttpRequest): The HTTP request object containing the webhook payload.

    Returns:
        HttpResponse: An HTTP response indicating the result of the webhook processing.
    """

    payload = request.body
    headers = request.headers
    # Verify webhook signature
    transmission_id = headers.get("Paypal-Transmission-Id")
    transmission_time = headers.get("Paypal-Transmission-Time")
    cert_url = headers.get("Paypal-Cert-Url")
    auth_algo = headers.get("Paypal-Auth-Algo")
    transmission_sig = headers.get("Paypal-Transmission-Sig")
    webhook_id = settings.PAYPAL_WEBHOOK_ID
    valid_sig = verify_webhook_signature(
        transmission_sig,
        transmission_id,
        transmission_time,
        webhook_id,
        payload.decode("utf-8"),
        cert_url,
        auth_algo,
    )
    if valid_sig:
        event = json.loads(payload)

        if event["event_type"] == "CHECKOUT.ORDER.APPROVED":
            # Handle payment completed event
            resource = event["resource"]
            purchase_unit = resource["purchase_units"][0]
            amount_paid = decimal.Decimal(purchase_unit["amount"]["value"])
            order = (
                Order.objects.prefetch_related("orderitems")
                .prefetch_related("orderitems__product")
                .get_or_none(tx_ref=purchase_unit["reference_id"])
            )
            if not order:
                return HttpResponse(status=200)
            if order.payment_status != "SUCCESSFUL":
                user = order.user
                amount_payable = order.get_cart_total
                if amount_paid < amount_payable:
                    # You made an invalid payment
                    EmailUtil.send_payment_failed_email(
                        user.full_name, user.email, amount_paid
                    )
                    order.payment_status = "FAILED"
                    order.save()
                    return HttpResponse(status=200)

                order.payment_status = "SUCCESSFUL"
                order.save()

                update_product_in_stock(order.orderitems.all())
                # Send email
                EmailUtil.send_payment_success_email(
                    user.full_name, user.email, amount_payable
                )
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=200)
