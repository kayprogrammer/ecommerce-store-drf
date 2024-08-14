from drf_spectacular.utils import OpenApiParameter, OpenApiExample, OpenApiResponse

from apps.common.exceptions import ErrorCode

RESPONSE_TYPE = {"application/json"}
ERR_RESPONSE_STATUS = "failure"
SUCCESS_RESPONSE_STATUS = "success"

PAGINATED_RESPONSE_EXAMPLE = {"per_page": 100, "current_page": 1, "last_page": 10}

UUID_EXAMPLE = "7d26157c-b7ed-4b4f-83de-f7e40e1caca0"

DATETIME_EXAMPLE = "2024-08-11T09:00:00"


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


def non_existent_response_example(object_type):
    return OpenApiResponse(
        response=RESPONSE_TYPE,
        description=f"{object_type} Does Not Exist",
        examples=[
            OpenApiExample(
                name="Non-existent Response",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "code": ErrorCode.NON_EXISTENT,
                    "message": f"{object_type} does not exist!",
                },
            )
        ],
    )


UNPROCESSABLE_ENTITY_EXAMPLE = (
    OpenApiResponse(
        response=RESPONSE_TYPE,
        description="Invalid Entry",
        examples=[
            OpenApiExample(
                name="Invalid Entry",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Invalid Entry",
                    "data": {"field": "value"},
                },
            ),
        ],
    ),
)
