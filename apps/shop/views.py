from adrf.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from apps.common.exceptions import ErrorCode, RequestError
from apps.common.paginators import CustomPagination
from apps.common.permissions import IsAuthenticatedCustom
from apps.common.responses import CustomResponse
from apps.common.schema_examples import page_parameter_example
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.shop.models import Category, Product, Review
from apps.shop.schema_examples import (
    CATEGORIES_RESPONSE,
    PRODUCT_RESPONSE,
    PRODUCTS_RESPONSE,
    REVIEW_RESPONSE_EXAMPLE,
)
from apps.shop.serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductsResponseDataSerializer,
    ReviewSerializer,
)
from apps.shop.utils import color_size_filter_products
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
        parameters=[
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
        ],
    )
    async def get(self, request, *args, **kwargs):
        """
        Handle async GET requests to fetch all products, with optional filtering.

        Args:
            request: The request object.

        Returns:
            CustomResponse: A response containing serialized and paginated product data.
        """
        name_filter = request.GET.get("name")

        products = (
            Product.objects.select_related("category", "seller")
            .prefetch_related("sizes", "colors")
            .annotate(**REVIEWS_AND_RATING_ANNOTATION)
            .filter(in_stock__gt=0)
        )
        if name_filter:
            products = products.filter(name__icontains=name_filter)
        products = await sync_to_async(list)(
            color_size_filter_products(
                products.order_by("-created_at"),
                request.GET.getlist("size"),
                request.GET.getlist("color"),
            )
        )

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
        product = await (
            Product.objects.select_related("category", "seller")
            .prefetch_related("sizes", "colors", "reviews", "reviews__user")
            .annotate(**REVIEWS_AND_RATING_ANNOTATION)
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
            .annotate(**REVIEWS_AND_RATING_ANNOTATION)
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
        return []
