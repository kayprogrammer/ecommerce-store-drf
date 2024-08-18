import json
from typing import Dict, Union

from django.conf import settings
import requests
from apps.shop.models import Product, ShippingAddress
from asgiref.sync import sync_to_async
from apps.common.utils import REVIEWS_AND_RATING_WISHLISTED_CARTED_ANNOTATION


def color_size_filter_products(products_original, sizes, colors):
    products = products_original
    sized_products = None
    colored_products = None

    if len(sizes) > 0:
        sized_products = products_original.exclude(sizes=None)
        if not "ALL" in sizes:  # incase of an ALL option
            sized_products = products_original.filter(sizes__value__in=sizes)
        products = sized_products

    if len(colors) > 0:
        colored_products = products_original.exclude(colors=None)
        if not "ALL" in colors:
            colored_products = products_original.filter(colors__value__in=colors)
        products = colored_products

    if sized_products and colored_products:
        products = sized_products | colored_products
    return products.distinct()


async def fetch_products(request, user, guest, extra_filter: Dict = None):
    name_filter = request.GET.get("name")
    products = (
        Product.objects.select_related("category", "seller")
        .prefetch_related("sizes", "colors")
        .annotate(**REVIEWS_AND_RATING_WISHLISTED_CARTED_ANNOTATION(user, guest))
        .filter(in_stock__gt=0)
    )
    if name_filter:
        products = products.filter(name__icontains=name_filter)
    if extra_filter:
        products = products.filter(**extra_filter)
    products = await sync_to_async(list)(
        color_size_filter_products(
            products.order_by("-created_at"),
            request.GET.getlist("size"),
            request.GET.getlist("color"),
        )
    )
    return products


def append_shipping_details(data: Dict, shipping: ShippingAddress):
    fields_to_update = [
        "full_name",
        "email",
        "phone",
        "address",
        "city",
        "state",
        "country",
        "zipcode",
    ]
    for field in fields_to_update:
        value = getattr(shipping, field)
        if field == "country":
            data["country"] = value.name
        else:
            data[field] = value
    return data


def get_access_token():
    auth_response = requests.post(
        settings.PAYPAL_AUTH_URL,
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US",
        },
        data={
            "grant_type": "client_credentials",
        },
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
    )
    auth_response.raise_for_status()
    return auth_response.json()["access_token"]


def verify_webhook_signature(
    expected_signature,
    transmission_id,
    transmission_time,
    webhook_id,
    event,
    cert_url,
    auth_algo,
):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_access_token()}",
    }
    data = json.dumps(
        {
            "transmission_id": transmission_id,
            "transmission_time": transmission_time,
            "cert_url": cert_url,
            "auth_algo": auth_algo,
            "transmission_sig": expected_signature,
            "webhook_id": webhook_id,
            "webhook_event": json.loads(event),
        }
    )
    response = requests.post(
        settings.PAYPAL_WEBHOOK_VERIFICATION_URL, headers=headers, data=data
    )
    response.raise_for_status()
    verification_status = response.json().get("verification_status")
    return verification_status == "SUCCESS"


def update_product_in_stock(orderitems):
    products_to_update = []
    for item in orderitems:
        product = item.product
        # Ensure in_stock doesn't go below 0
        new_stock = max(product.in_stock - item.quantity, 0)
        if new_stock != product.in_stock:
            product.in_stock = new_stock
            products_to_update.append(product)
    Product.objects.bulk_update(products_to_update, ["in_stock"])
