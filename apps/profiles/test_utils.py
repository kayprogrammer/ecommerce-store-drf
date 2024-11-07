from apps.accounts.test_utils import TestAccountUtil
from apps.shop.models import ShippingAddress


class TestProfileUtil:
    def shipping_address(user):
        data = {
            "full_name": "Test User",
            "email": "testuser@example.com",
            "phone": "+23412345678",
            "address": "123, Street",
            "city": "Whatever city",
            "state": "Lagos",
            "country": TestAccountUtil.country(),
            "zipcode": "123456",
        }
        shipping_addr, _ = ShippingAddress.objects.get_or_create(
            user=user, defaults=data
        )
        return shipping_addr
