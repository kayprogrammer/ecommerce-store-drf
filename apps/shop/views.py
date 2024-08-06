from adrf.views import APIView
from drf_spectacular.utils import extend_schema
from apps.common.exceptions import ErrorCode, RequestError
from apps.common.paginators import CustomPagination
from apps.common.responses import CustomResponse
from apps.common.schema_examples import page_parameter_example
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.shop.models import Category, Product
from apps.shop.schema_examples import (
    CATEGORIES_RESPONSE,
    PRODUCT_RESPONSE,
    PRODUCTS_RESPONSE,
)
from apps.shop.serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductSerializer,
    ProductsResponseDataSerializer,
)
from apps.shop.utils import colour_size_filter_products
from asgiref.sync import sync_to_async

tags = ["Shop"]


class CategoriesView(APIView):
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
        categories = await sync_to_async(list)(Category.objects.all())
        serializer = self.serializer_class(categories, many=True)
        return CustomResponse.success(
            message="Categories fetched successfully", data=serializer.data
        )


class ProductsView(APIView):
    serializer_class = ProductsResponseDataSerializer
    paginator_class = CustomPagination()

    @extend_schema(
        summary="Products Fetch",
        description="""
            This endpoint returns all products.
            Products can be filtered by name, sizes or colors
        """,
        tags=tags,
        responses=PRODUCTS_RESPONSE,
        parameters=page_parameter_example("products", 100),
    )
    async def get(self, request, *args, **kwargs):
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
            colour_size_filter_products(
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
    serializer_class = ProductDetailSerializer
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
            .prefetch_related("sizes", "colors", "reviews", "reviews__user")
            .annotate(**REVIEWS_AND_RATING_ANNOTATION)
            .filter(category_id=product.category_id, in_stock__gt=0)
            .exclude(id=product.id)[:10]
        )
        product.reviews_data = paginated_data
        serializer = self.serializer_class(product)
        return CustomResponse.success(
            message="Product Details Fetched Successfully", data=serializer.data
        )
