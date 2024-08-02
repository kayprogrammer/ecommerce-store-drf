from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample

from apps.accounts.schema_examples import TOKEN_EXAMPLE


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Tokens request",
            value={
                "token": TOKEN_EXAMPLE,
            },
            request_only=True,
        ),
    ]
)
class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
