from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes,
)
from drf_spectacular.plumbing import (
    build_choice_field,
    build_array_type,
    build_basic_type,
)

from apps.common.exceptions import ErrorCode
from rest_framework import serializers, fields

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


UNPROCESSABLE_ENTITY_EXAMPLE = OpenApiResponse(
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
)

FIELD_TYPE_MAP = {
    fields.CharField: OpenApiTypes.STR,
    fields.EmailField: OpenApiTypes.EMAIL,
    fields.IntegerField: OpenApiTypes.INT,
    fields.FloatField: OpenApiTypes.FLOAT,
    fields.BooleanField: OpenApiTypes.BOOL,
    fields.DateField: OpenApiTypes.DATE,
    fields.DateTimeField: OpenApiTypes.DATETIME,
    fields.URLField: OpenApiTypes.URI,
    fields.FileField: OpenApiTypes.BINARY,
    fields.DictField: OpenApiTypes.OBJECT,
}


def generate_field_properties_for_swagger(
    serializer_class: serializers.Serializer, example_data
):
    field_properties = {}
    required_fields = []
    for field_name, value in example_data.items():
        field_class = serializer_class.fields.get(field_name)
        field_property_data = {}
        if isinstance(field_class, fields.ChoiceField):
            field_property_data = build_choice_field(field_class)
        elif isinstance(field_class, fields.ListField):
            field_property_data = build_array_type(value)
        else:
            field_property_data = build_basic_type(FIELD_TYPE_MAP[type(field_class)])
        field_properties[field_name] = field_property_data | {"example": value}
        if field_class.required:
            required_fields.append(field_name)
    return field_properties, required_fields
