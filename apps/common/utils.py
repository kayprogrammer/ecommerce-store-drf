from django.db.models import Avg, Value, FloatField, Count, OuterRef, Exists
from django.db.models.functions import Coalesce
from rest_framework.serializers import Serializer
from apps.accounts.models import GuestUser
from apps.shop.models import Wishlist


def REVIEWS_AND_RATING_WISHLISTED_CARTED_ANNOTATION(user, guest):
    wishlist_subquery = Wishlist.objects.filter(
        product=OuterRef("pk"), user=user, guest=guest
    )
    return {
        "reviews_count": Count("reviews"),
        "avg_rating": Coalesce(
            Avg("reviews__rating"), Value(0), output_field=FloatField()
        ),
        "wishlisted": Exists(wishlist_subquery),
    }


def get_user_or_guest(user):
    if isinstance(user, GuestUser):
        return None, user
    return user, None


def validate_request_data(request, serializer_class: Serializer):
    serializer = serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def set_dict_attr(obj, data):
    for attr, value in data.items():
        setattr(obj, attr, value)
    return obj
