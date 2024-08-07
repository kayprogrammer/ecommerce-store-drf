from django.db.models import Avg, Value, FloatField, Count
from django.db.models.functions import Coalesce

from apps.accounts.models import GuestUser

REVIEWS_AND_RATING_ANNOTATION = {
    "reviews_count": Count("reviews"),
    "avg_rating": Coalesce(Avg("reviews__rating"), Value(0), output_field=FloatField()),
}


def get_user_or_guest(user):
    if isinstance(user, GuestUser):
        return None, user
    return user, None
