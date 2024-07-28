from adrf.views import APIView
from drf_spectacular.utils import extend_schema
from apps.common.responses import CustomResponse

from apps.common.serializers import SuccessResponseSerializer
from .models import Message, SiteDetail, Subscriber
from .serializers import (
    MessageSerializer,
    SiteDetailSerializer,
    SiteDetailResponseSerializer,
    SubscriberSerializer,
)

tags = ["General"]


class SiteDetailView(APIView):
    """
    API view for retrieving site details.

    This view provides an endpoint to fetch details about the site/application,
    including general information and social media links. It uses asynchronous
    operations to handle database interactions.

    Attributes:
        serializer_class (Type[SiteDetailSerializer]): The serializer class used to validate and serialize the SiteDetail model.

    Methods:
        get(request: Request) -> Response:
            Retrieves the site details, serializes the data, and returns it in a successful response.
            Uses the `SiteDetailSerializer` to serialize the `SiteDetail` instance and returns it in a `CustomResponse`.

    Schema:
        The `@extend_schema` decorator is used to define the OpenAPI schema for this endpoint.

    """

    serializer_class = SiteDetailSerializer

    @extend_schema(
        summary="Retrieve site details",
        description="This endpoint retrieves a few details of the site/application",
        tags=tags,
        responses=SiteDetailResponseSerializer,
    )
    async def get(self, request):
        """
        Handle GET requests to fetch site details.

        This method asynchronously retrieves the `SiteDetail` instance, creates one if it does not exist,
        serializes the data using `SiteDetailSerializer`, and returns it in a `CustomResponse`.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A `CustomResponse` containing the serialized site details.
        """
        sitedetail, created = await SiteDetail.objects.aget_or_create()
        serializer = self.serializer_class(sitedetail)
        return CustomResponse.success(
            message="Site Details fetched", data=serializer.data
        )


class SubscribeView(APIView):
    """
    API view for subscribing to our newsletter.
    """

    serializer_class = SubscriberSerializer

    @extend_schema(
        summary="Subscribe to newsletter",
        description="This endpoint adds an email to our newsletter.",
        tags=tags,
        responses=SuccessResponseSerializer,
    )
    async def post(self, request):
        """
        Handle async POST requests to subscribe user to our newsletter.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        await Subscriber.objects.aget_or_create(
            email=serializer.validated_data["email"]
        )
        return CustomResponse.success(message="Subscribed successfully")


class MessageView(APIView):
    """
    API view for allowing people to send us a message.
    """

    serializer_class = MessageSerializer

    @extend_schema(
        summary="Send us a message",
        description="This endpoint allows anyone to send us a message.",
        tags=tags,
        responses=SuccessResponseSerializer,
    )
    async def post(self, request):
        """
        Handle async POST requests to create a message.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        await Message.objects.acreate(**serializer.validated_data)
        return CustomResponse.success(message="Message sent successfully")
