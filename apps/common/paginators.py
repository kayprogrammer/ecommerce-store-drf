from django.core.paginator import InvalidPage
from rest_framework.pagination import PageNumberPagination
from apps.common.exceptions import ErrorCode, RequestError


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class extending PageNumberPagination.

    Attributes:
        page_size_query_param (str): Optional parameter to allow clients to override the page size.
    """

    page_size_query_param = (
        "page_size"  # Optional: allow clients to override the page size
    )

    def paginate_queryset(self, queryset, request):
        per_page = request.GET.get("per_page", 100)
        current_page = request.GET.get("current_page", 1)

        """
        Paginate a queryset if required, either returning a page object,
        or `None` if pagination is not configured for this view.

        Args:
            queryset (QuerySet): The queryset to paginate.
            request (HttpRequest): The current request object.
            view (APIView, optional): The view that is being processed. Defaults to None.

        Returns:
            dict: A dictionary containing pagination details and the items on the current page,
            or `None` if pagination is not configured.
        """

        paginator = self.django_paginator_class(queryset, per_page)
        try:
            self.page = paginator.page(current_page)
        except InvalidPage:
            raise RequestError(
                err_code=ErrorCode.INVALID_PAGE, err_msg="Invalid Page", status_code=404
            )

        self.request = request
        return {
            "items": list(self.page),
            "per_page": per_page,
            "current_page": current_page,
            "last_page": paginator.num_pages,
        }
