from adrf.views import APIView
from drf_spectacular.utils import extend_schema
from apps.common.exceptions import NotFoundError, ValidationErr
from apps.common.paginators import CustomPagination
from apps.common.permissions import IsAuthenticatedCustom
from apps.common.utils import set_dict_attr
from apps.common.responses import CustomResponse
from apps.shop.models import Country, Order, ShippingAddress
from .schema_examples import (
    ACCOUNT_DEACTIVATION_RESPONSE_EXAMPLE,
    ORDERS_PARAM_EXAMPLE,
    ORDERS_RESPONSE_EXAMPLE,
    PROFILE_RESPONSE_EXAMPLE,
    PROFILE_UPDATE_RESPONSE_EXAMPLE,
    SHIPPING_ADDRESS_CREATE_RESPONSE_EXAMPLE,
    SHIPPING_ADDRESS_DELETE_RESPONSE_EXAMPLE,
    SHIPPING_ADDRESS_GET_RESPONSE_EXAMPLE,
    SHIPPING_ADDRESS_UPDATE_RESPONSE_EXAMPLE,
    SHIPPING_ADDRESSES_RESPONSE_EXAMPLE,
)
from asgiref.sync import sync_to_async

from .serializers import (
    OrdersResponseDataSerializer,
    ProfileSerializer,
    ShippingAddressSerializerWithID,
)

tags = ["Profiles"]


class ProfileView(APIView):
    """
    A asynchronous view to handle the retrieval and updating of user profiles.

    Attributes:
        serializer_class (ProfileSerializer): The serializer class used to validate and serialize profile data.
        permission_classes (tuple): Permissions required to access this view, in this case, custom authentication.

    Methods:
        get(request):
            Retrieves the profile of the authenticated user.

        put(request):
            Updates the profile of the authenticated user.
    """

    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticatedCustom,)

    @extend_schema(
        summary="Retrieve Profile",
        description="""
            This endpoint allows a user to retrieve his/her profile.
        """,
        tags=tags,
        responses=PROFILE_RESPONSE_EXAMPLE,
    )
    async def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return CustomResponse.success(
            message="User Profile Fetched", data=serializer.data
        )

    @extend_schema(
        summary="Update Profile",
        description="""
            This endpoint allows a user to update his/her profile.
        """,
        tags=tags,
        request={"multipart/form-data": serializer_class},
        responses=PROFILE_UPDATE_RESPONSE_EXAMPLE,
    )
    async def put(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = set_dict_attr(user, serializer.validated_data)
        await user.asave()
        serializer = self.serializer_class(user)
        return CustomResponse.success(
            message="User Profile Updated", data=serializer.data
        )

    @extend_schema(
        summary="Deactivate account",
        description="""
            This endpoint allows a user to deactivate his/her account.
        """,
        tags=tags,
        responses=ACCOUNT_DEACTIVATION_RESPONSE_EXAMPLE,
    )
    async def delete(self, request):
        user = request.user
        user.is_active = False
        await user.asave()
        return CustomResponse.success(message="User Account Deactivated")


class ShippingAddressesView(APIView):
    """
    View for handling shipping addresses associated with a user.

    This view allows users to fetch all their shipping addresses or create new ones.

    Attributes:
        serializer_class (ShippingAddressSerializerWithID): Serializer class for handling shipping address data.
        permission_classes (list): List of permission classes, allowing only authenticated users.

    Methods:
        get(request, *args, **kwargs): Fetch all shipping addresses associated with the authenticated user.
        post(request, *args, **kwargs): Create a new shipping address for the authenticated user.
    """

    serializer_class = ShippingAddressSerializerWithID
    permission_classes = [IsAuthenticatedCustom]

    @extend_schema(
        summary="Shipping Addresses Fetch",
        description="""
            This endpoint returns all shipping addresses associated with a user.
        """,
        tags=tags,
        responses=SHIPPING_ADDRESSES_RESPONSE_EXAMPLE,
    )
    async def get(self, request, *args, **kwargs):
        user = request.user
        shipping_addresses = await sync_to_async(list)(
            ShippingAddress.objects.select_related("country").filter(user=user)
        )
        serializer = self.serializer_class(shipping_addresses, many=True)
        return CustomResponse.success(
            message="Shipping addresses returned", data=serializer.data
        )

    @extend_schema(
        summary="Create Shipping Address",
        description="""
            This endpoint allows a user to create a shipping address.
        """,
        tags=tags,
        responses=SHIPPING_ADDRESS_CREATE_RESPONSE_EXAMPLE,
    )
    async def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        country = data.pop("country")
        country = await Country.objects.aget_or_none(name=country)
        if not country:
            raise ValidationErr("country", "Invalid country selected")
        shipping_address, _ = await ShippingAddress.objects.select_related(
            "country"
        ).aget_or_create(user=user, country=country, **data)
        serializer = self.serializer_class(shipping_address)
        return CustomResponse.success(
            message="Shipping address created successfully",
            data=serializer.data,
            status_code=201,
        )


class ShippingAddressView(APIView):
    """
    View for handling a single shipping address associated with a user.

    This view allows users to fetch, update, or delete a specific shipping address.

    Attributes:
        serializer_class (ShippingAddressSerializerWithID): Serializer class for handling shipping address data.
        permission_classes (list): List of permission classes, allowing only authenticated users.

    Methods:
        get(request, *args, **kwargs): Fetch a single shipping address associated with the authenticated user.
        put(request, *args, **kwargs): Update a specific shipping address for the authenticated user.
        delete(request, *args, **kwargs): Delete a specific shipping address for the authenticated user.
    """

    serializer_class = ShippingAddressSerializerWithID
    permission_classes = [IsAuthenticatedCustom]

    async def get_object(self, user, shipping_id):
        shipping_address = await ShippingAddress.objects.select_related(
            "country"
        ).aget_or_none(user=user, id=shipping_id)
        if not shipping_address:
            raise NotFoundError("User does not have a shipping address with that ID")
        return shipping_address

    @extend_schema(
        summary="Shipping Address Fetch",
        description="""
            This endpoint returns a single shipping address associated with a user.
        """,
        tags=tags,
        responses=SHIPPING_ADDRESS_GET_RESPONSE_EXAMPLE,
    )
    async def get(self, request, *args, **kwargs):
        user = request.user
        shipping_address = await self.get_object(user, kwargs["id"])
        serializer = self.serializer_class(shipping_address)
        return CustomResponse.success(
            message="Shipping address returned", data=serializer.data
        )

    @extend_schema(
        summary="Update Shipping Address",
        description="""
            This endpoint allows a user to update his/her shipping address.
        """,
        tags=tags,
        responses=SHIPPING_ADDRESS_UPDATE_RESPONSE_EXAMPLE,
    )
    async def put(self, request, *args, **kwargs):
        user = request.user
        shipping_address = await self.get_object(user, kwargs["id"])
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        country = data.pop("country")
        country = await Country.objects.aget_or_none(name=country)
        if not country:
            raise ValidationErr("country", "Invalid country selected")
        shipping_address.country = country
        shipping_address = set_dict_attr(shipping_address, data)
        await shipping_address.asave()
        serializer = self.serializer_class(shipping_address)
        return CustomResponse.success(
            message="Shipping address updated successfully",
            data=serializer.data,
            status_code=200,
        )

    @extend_schema(
        summary="Delete Shipping Address",
        description="""
            This endpoint allows a user to delete his/her shipping address.
        """,
        tags=tags,
        responses=SHIPPING_ADDRESS_DELETE_RESPONSE_EXAMPLE,
    )
    async def delete(self, request, *args, **kwargs):
        user = request.user
        shipping_address = await ShippingAddress.objects.aget_or_none(
            user=user, id=kwargs["id"]
        )
        if not shipping_address:
            raise NotFoundError("User does not have a shipping address with that ID")
        await shipping_address.adelete()
        return CustomResponse.success(message="Shipping address deleted successfully")


class OrdersView(APIView):
    """
    API view to fetch all orders for a user.

    Methods:
        get: Asynchronously fetches and returns all orders, with optional filtering by payment status, delivery status.
    """

    permission_classes = [IsAuthenticatedCustom]
    serializer_class = OrdersResponseDataSerializer
    paginator_class = CustomPagination()

    @extend_schema(
        summary="Orders Fetch",
        description="""
            This endpoint returns all orders for a particular user.
            Orders can be filtered by payment status or delivery status.
        """,
        tags=tags,
        responses=ORDERS_RESPONSE_EXAMPLE,
        parameters=ORDERS_PARAM_EXAMPLE,
    )
    async def get(self, request):
        user = request.user
        payment_status = request.GET.get("payment_status")
        delivery_status = request.GET.get("delivery_status")
        filter_ = {"user": user}
        if payment_status:
            filter_["payment_status"] = payment_status
        if delivery_status:
            filter_["delivery_status"] = delivery_status

        orders = await sync_to_async(list)(
            Order.objects.filter(**filter_)
            .select_related("user", "coupon")
            .prefetch_related("orderitems", "orderitems__product")
            .order_by("-created_at")
        )
        paginated_data = self.paginator_class.paginate_queryset(orders, request)
        serializer = self.serializer_class(paginated_data)
        return CustomResponse.success(
            message="Orders Fetched Successfully", data=serializer.data
        )
