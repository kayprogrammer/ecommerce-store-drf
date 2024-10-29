from apps.shop.models import Category


class TestShopUtil:
    def category():
        category, _ = Category.objects.get_or_create(name="Test Category")
        return category