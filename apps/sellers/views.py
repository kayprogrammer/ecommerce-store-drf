from adrf.views import APIView
from drf_spectacular.utils import extend_schema

from apps.common.decorators import aatomic
from apps.common.exceptions import NotFoundError, ValidationErr
from apps.common.paginators import CustomPagination
from apps.common.permissions import (
    IsAuthenticatedBuyerCustom,
    IsAuthenticatedOrGuestCustom,
)
from apps.common.responses import CustomResponse
from apps.common.utils import get_user_or_guest, validate_request_data
from apps.shop.schema_examples import PRODUCTS_PARAM_EXAMPLE
from apps.shop.serializers import ProductsResponseDataSerializer
from apps.shop.utils import fetch_products
from .models import Seller
from .schema_examples import (
    SELLER_APPLICATION_REQUEST_EXAMPLE,
    SELLER_APPLICATION_RESPONSE_EXAMPLE,
    SELLER_PRODUCTS_RESPONSE,
)
from .serializers import SellerSerializer
from apps.shop.models import Category, Country
from asgiref.sync import sync_to_async

tags = ["Sellers"]


class SellersApplicationView(APIView):
    """
    A asynchronous view to handle the creation and update of sellers application.

    Attributes:
        serializer_class (SellerSerializer): The serializer class used to validate and serialize profile data.
        permission_classes (tuple): Permissions required to access this view, in this case, custom authentication.
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
    permission_classes = [IsAuthenticatedOrGuestCustom]
    serializer_class = ProductsResponseDataSerializer
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
