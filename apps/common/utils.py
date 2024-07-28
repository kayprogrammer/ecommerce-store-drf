from django.db.models import Avg, Value, FloatField, Count
from django.db.models.functions import Coalesce

REVIEWS_AND_RATING_ANNOTATION = {
    "reviews_count": Count("reviews"),
    "avg_rating": Coalesce(Avg("reviews__rating"), Value(0), output_field=FloatField()),
}
