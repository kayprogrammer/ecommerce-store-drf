from adrf.views import APIView
from drf_spectacular.utils import extend_schema
from apps.common.responses import CustomResponse
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.shop.models import Product
from apps.shop.serializers import ProductSerializer
from apps.shop.utils import colour_size_filter_products
from asgiref.sync import sync_to_async


class ProductsView(APIView):
    serializer_class = ProductSerializer

    async def get(self, request, *args, **kwargs):
        name_filter = request.GET.get("name")
        products = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).filter(
            in_stock__gt=0
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

        serializer = self.serializer_class(products, many=True)
        return CustomResponse.success(message="Products fetched", data=serializer.data)
