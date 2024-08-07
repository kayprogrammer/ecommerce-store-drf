from drf_spectacular.utils import OpenApiParameter

RESPONSE_TYPE = {"application/json"}
ERR_RESPONSE_STATUS = "failure"
SUCCESS_RESPONSE_STATUS = "success"

PAGINATED_RESPONSE_EXAMPLE = {"per_page": 100, "current_page": 1, "last_page": 10}

UUID_EXAMPLE = "7d26157c-b7ed-4b4f-83de-f7e40e1caca0"


def page_parameter_example(item, page_amount_default):
    return [
        OpenApiParameter(
            name="current_page",
            description=f"Retrieve a particular page of {item}. Defaults to 1",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="per_page",
            description=f"The amount of {item} per page you want to display. Defaults to {page_amount_default}",
            required=False,
            type=int,
        ),
    ]
