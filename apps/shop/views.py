from adrf.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from apps.common.decorators import aatomic
from apps.common.exceptions import ErrorCode, RequestError, ValidationError
from apps.common.paginators import CustomPagination
from apps.common.permissions import IsAuthenticatedCustom, IsAuthenticatedOrGuestCustom
from apps.common.responses import CustomResponse
from apps.common.schema_examples import page_parameter_example
from apps.common.utils import (
    REVIEWS_AND_RATING_WISHLISTED_CARTED_ANNOTATION,
    get_user_or_guest,
)
from apps.shop.models import Category, OrderItem, Product, Review, Wishlist
from apps.shop.schema_examples import (
    CART_RESPONSE_EXAMPLE,
    CATEGORIES_RESPONSE,
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
    OrderItemSerializer,
    OrderItemsResponseDataSerializer,
    ProductDetailSerializer,
    ProductsResponseDataSerializer,
    ReviewSerializer,
    ToggleCartItemSerializer,
)
from apps.shop.utils import fetch_products
from asgiref.sync import sync_to_async

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
            Product.objects.select_related("category", "seller")
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
                "product", "size", "color"
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
            raise ValidationError("slug", "No Product with that slug")
        if size:
            size = await product.sizes.aget_or_none(value=size)
            if not size:
                raise ValidationError("size", "Invalid size selected")

        if color:
            color = await product.colors.aget_or_none(value=color)
            if not color:
                raise ValidationError("color", "Invalid color selected")

        orderitem, created = await OrderItem.objects.select_related(
            "size", "color"
        ).aupdate_or_create(
            user=user,
            guest=guest,
            order_id=None,
            product=product,
            size=size,
            color=color,
            defaults={"quantity": quantity},
        )
        print("Haaalala")
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
            serializer = self.item_serializer_class(orderitem)
            data = serializer.data
        return CustomResponse.success(
            message=f"Item {resp_message_substring} Cart",
            data=data,
            status_code=status_code,
        )
