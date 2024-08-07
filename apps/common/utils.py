from django.db.models import Avg, Value, FloatField, Count, OuterRef, Exists
from django.db.models.functions import Coalesce

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
