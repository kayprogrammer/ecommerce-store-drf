from adrf.views import APIView
from drf_spectacular.utils import extend_schema
from django.db.models import Prefetch
from apps.common.decorators import aatomic
from apps.common.exceptions import NotFoundError, ValidationErr
from apps.common.paginators import CustomPagination
from apps.common.permissions import (
    IsAuthenticatedBuyerCustom,
    IsAuthenticatedOrGuestCustom,
    IsAuthenticatedSellerCustom,
)
from apps.common.responses import CustomResponse
from apps.common.utils import (
    REVIEWS_AND_RATING_WISHLISTED_CARTED_ANNOTATION,
    get_user_or_guest,
    set_dict_attr,
    validate_request_data,
)
from apps.profiles.schema_examples import ORDERS_PARAM_EXAMPLE, ORDERS_RESPONSE_EXAMPLE
from apps.profiles.serializers import OrdersResponseDataSerializer
from apps.sellers.utils import validate_category_sizes_colors
from apps.shop.schema_examples import PRODUCTS_PARAM_EXAMPLE
from apps.shop.serializers import ProductSerializer, ProductsResponseDataSerializer
from apps.shop.utils import fetch_products
from .models import Seller
from .schema_examples import (
    PRODUCT_CREATE_REQUEST_EXAMPLE,
    PRODUCT_CREATE_RESPONSE_EXAMPLE,
    PRODUCT_DELETE_RESPONSE_EXAMPLE,
    PRODUCT_UPDATE_RESPONSE_EXAMPLE,
    SELLER_APPLICATION_REQUEST_EXAMPLE,
    SELLER_APPLICATION_RESPONSE_EXAMPLE,
    SELLER_PRODUCTS_RESPONSE,
)
from .serializers import ProductCreateSerializer, SellerSerializer
from apps.shop.models import Category, Color, Country, Order, OrderItem, Product, Size
from asgiref.sync import sync_to_async

tags = ["Sellers"]


class SellersApplicationView(APIView):
    """
    A asynchronous view to handle the creation and update of sellers application.

    Attributes:
        serializer_class (SellerSerializer): The serializer class used to validate and serialize profile data.
        permission_classes (IsAuthenticatedBuyerCustom): Permissions required to access this view, in this case, buyers only.
    """

    serializer_class_ = SellerSerializer
    permission_classes = (IsAuthenticatedBuyerCustom,)

    @extend_schema(
        summary="Apply to become a seller",
        description="""
            This endpoint allows a buyer to apply to become a seller.
        """,
        tags=tags,
        request=SELLER_APPLICATION_REQUEST_EXAMPLE,
        responses=SELLER_APPLICATION_RESPONSE_EXAMPLE,
    )
    @aatomic
    async def post(self, request):
        user = request.user
        data = validate_request_data(request, self.serializer_class_)
        country = data.pop("country")
        country = await Country.objects.aget_or_none(name=country)
        if not country:
            raise ValidationErr("country", "Invalid country selected")
        data["country"] = country
        product_categories = data.pop("product_categories")
        product_categories = product_categories["name"]
        categories = await sync_to_async(list)(
            Category.objects.filter(name__in=product_categories)
        )
        if len(categories) < 1:
            raise ValidationErr("product_categories", "No valid category was selected")
        application, _ = await Seller.objects.aupdate_or_create(
            user=user, defaults=data
        )
        await application.product_categories.aset(categories)
        application.product_categories_ = product_categories
        serializer = self.serializer_class_(application)
        return CustomResponse.success(
            message="Application submitted successfully", data=serializer.data
        )


class ProductsBySellerView(APIView):
    serializer_class = ProductsResponseDataSerializer
    serializer_entry_class = ProductCreateSerializer
    paginator_class = CustomPagination()

    @extend_schema(
        summary="Seller Products Fetch",
        description="""
            This endpoint returns all products from a seller.
            Products can be filtered by name, sizes or colors.
        """,
        tags=tags,
        responses=SELLER_PRODUCTS_RESPONSE,
        parameters=PRODUCTS_PARAM_EXAMPLE,
    )
    async def get(self, request, *args, **kwargs):
        user, guest = get_user_or_guest(request.user)
        seller = await Seller.objects.aget_or_none(
            slug=kwargs["slug"], is_approved=True
        )
        if not seller:
            raise NotFoundError(err_msg="No approved seller with that slug")
        products = await fetch_products(request, user, guest, {"seller": seller})
        paginated_data = self.paginator_class.paginate_queryset(products, request)
        serializer = self.serializer_class(paginated_data)
        return CustomResponse.success(
            message="Seller Products Fetched Successfully", data=serializer.data
        )

    @extend_schema(
        summary="Products Update",
        description="""
            This endpoint updates a seller product.
        """,
        tags=tags,
        request=PRODUCT_CREATE_REQUEST_EXAMPLE,
        responses=PRODUCT_UPDATE_RESPONSE_EXAMPLE,
    )
    @aatomic
    async def patch(self, request, *args, **kwargs):
        user = request.user
        product = await Product.objects.aget_or_none(
            seller=user.seller, slug=kwargs["slug"]
        )
        if not product:
            raise NotFoundError(err_msg="User owns no product with that slug")
        data = validate_request_data(request, self.serializer_entry_class, True)
        data, sizes, colors = await validate_category_sizes_colors(data)

        product = set_dict_attr(product, data)
        await product.asave()

        # Set sizes and colors
        await product.sizes.aadd(*sizes)
        await product.colors.aadd(*colors)

        # Return refreshed product
        product = await (
            Product.objects.select_related("category", "seller", "seller__user")
            .prefetch_related("sizes", "colors", "reviews", "reviews__user")
            .annotate(**REVIEWS_AND_RATING_WISHLISTED_CARTED_ANNOTATION(user, None))
            .aget(id=product.id)
        )
        serializer = ProductSerializer(product)
        return CustomResponse.success(
            message="Product Updated Successfully", data=serializer.data
        )

    @extend_schema(
        summary="Product Delete",
        description="""
            This endpoint allows a seller to delete a product.
        """,
        tags=tags,
        responses=PRODUCT_DELETE_RESPONSE_EXAMPLE,
    )
    @aatomic
    async def delete(self, request, *args, **kwargs):
        user = request.user
        product = await Product.objects.aget_or_none(
            seller=user.seller, slug=kwargs["slug"]
        )
        if not product:
            raise NotFoundError(err_msg="User owns no product with that slug")
        await product.adelete()
        return CustomResponse.success(message="Product Deleted Successfully")

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticatedOrGuestCustom()]
        return [IsAuthenticatedSellerCustom()]


class ProductCreateView(APIView):
    """
    A asynchronous view to handle the creation of products.

    Attributes:
        serializer_class (ProductCreateSerializer): The serializer class used to validate and serialize profile data.
        permission_classes (IsAuthenticatedSellerCustom): Permissions required to access this view, in this case, seller permissions.
    """

    serialier_class = ProductCreateSerializer
    serialier_resp_class = ProductSerializer
    permission_classes = (IsAuthenticatedSellerCustom,)

    @extend_schema(
        summary="Create a product",
        description="""
            This endpoint allows a seller to create a product.
        """,
        tags=tags,
        request=PRODUCT_CREATE_REQUEST_EXAMPLE,
        responses=PRODUCT_CREATE_RESPONSE_EXAMPLE,
    )
    @aatomic
    async def post(self, request):
        user = request.user
        data = validate_request_data(request, self.serialier_class)
        # Validate category, sizes and colors
        data, sizes, colors = await validate_category_sizes_colors(data)
        product = await Product.objects.acreate(seller=user.seller, **data)
        product.sizes_ = sizes
        product.colors_ = colors
        await product.sizes.aadd(*sizes)
        await product.colors.aadd(*colors)
        serializer = self.serialier_resp_class(product)
        return CustomResponse.success(
            message="Product created successfully",
            data=serializer.data,
            status_code=201,
        )


class OrdersView(APIView):
    """
    API view to fetch all orders attributed to a seller.

    Methods:
        get: Asynchronously fetches and returns all orders, with optional filtering by payment status, delivery status.
    """

    permission_classes = [IsAuthenticatedSellerCustom]
    serializer_class = OrdersResponseDataSerializer
    paginator_class = CustomPagination()

    @extend_schema(
        summary="Seller Orders Fetch",
        description="""
            This endpoint returns all orders for a particular seller.
            Orders can be filtered by payment status or delivery status.
        """,
        tags=tags,
        responses=ORDERS_RESPONSE_EXAMPLE,
        parameters=ORDERS_PARAM_EXAMPLE,
    )
    async def get(self, request):
        user = request.user
        seller = user.seller
        payment_status = request.GET.get("payment_status")
        delivery_status = request.GET.get("delivery_status")
        filter_ = {"orderitems__product__seller": seller}
        if payment_status:
            filter_["payment_status"] = payment_status
        if delivery_status:
            filter_["delivery_status"] = delivery_status

        # Fetch orders with orderitems that is targeted towards the seller products
        orders = await sync_to_async(list)(
            Order.objects.filter(**filter_)
            .select_related("user", "coupon")
            .prefetch_related(
                Prefetch(
                    "orderitems",
                    queryset=OrderItem.objects.filter(
                        product__seller=seller
                    ).select_related("product"),
                )
            )
            .order_by("-created_at")
        )
        paginated_data = self.paginator_class.paginate_queryset(orders, request)
        serializer = self.serializer_class(paginated_data)
        return CustomResponse.success(
            message="Orders Fetched Successfully", data=serializer.data
        )


# THINGS TO DO YOURSELF
# UPDATE ORDER
# INVENTORY MANAGEMENT
# PRODUCT REVIEWS

# I'LL MST LIKELY DO ALL THESE IN ANOTHER REPLICA
