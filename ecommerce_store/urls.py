from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from drf_spectacular.utils import extend_schema
from adrf.views import APIView

from apps.common.responses import CustomResponse
from apps.common.serializers import SuccessResponseSerializer
from rest_framework.response import Response
from debug_toolbar.toolbar import debug_toolbar_urls


class HealthCheckView(APIView):
    """
    View to check the health of the API.

    This endpoint provides a simple health check for the API to ensure that it is running.

    Methods:
        get(request): Responds with a success message "pong" to indicate that the API is healthy.
    """

    @extend_schema(
        "/",
        summary="API Health Check",
        description="This endpoint checks the health of the API",
        responses=SuccessResponseSerializer,
        tags=["HealthCheck"],
    )
    async def get(self, request):
        """
        Handle GET requests for the health check endpoint.

        Args:
            request (Request): The HTTP request object.

        Returns:
            JsonResponse: A success response with the message "pong".
        """
        return CustomResponse.success(message="pong")


def handler404(request, exception=None):
    """
    Custom 404 error handler.

    Returns a JSON response with a "Not Found" message and a 404 status code.

    Args:
        request (Request): The HTTP request object.
        exception (Exception, optional): The exception that caused the error.

    Returns:
        JsonResponse: The 404 error response.
    """
    response = JsonResponse({"status": "failure", "message": "Not Found"})
    response.status_code = 404
    return response


def handler500(request, exception=None):
    """
    Custom 500 error handler.

    Returns a JSON response with a "Server Error" message and a 500 status code.

    Args:
        request (Request): The HTTP request object.
        exception (Exception, optional): The exception that caused the error.

    Returns:
        JsonResponse: The 500 error response.
    """
    response = JsonResponse({"status": "failure", "message": "Server Error"})
    response.status_code = 500
    return response


handler404 = handler404
handler500 = handler500


class CustomSwaggerView(SpectacularSwaggerView):
    template_name = "custom_swagger.html"

    @extend_schema(exclude=True)
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        context = response.data
        # Add your custom context updates here
        context.update(
            {
                "google_client_id": settings.GOOGLE_CLIENT_ID,
                "facebook_app_id": settings.FACEBOOK_APP_ID,
            }
        )
        return Response(context, template_name=self.template_name)


urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "",
        CustomSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("admin/", admin.site.urls),
    path("api/v1/general/", include("apps.general.urls")),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/profiles/", include("apps.profiles.urls")),
    path("api/v1/shop/", include("apps.shop.urls")),
    path("api/v1/healthcheck/", HealthCheckView.as_view()),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()
