from django.contrib import admin

from apps.common.admin import BaseModelAdmin

from .models import (
    Category,
    Color,
    Coupon,
    Order,
    OrderItem,
    Product,
    Review,
    ShippingAddress,
    Country,
    Size,
)


class SizeAdmin(BaseModelAdmin):
    list_display = ("value", "created_at", "updated_at")
    list_filter = list_display


class CategoryAdmin(BaseModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    list_filter = list_display


class ProductAdmin(BaseModelAdmin):
    list_display = (
        "seller",
        "name",
        "desc",
        "price_old",
        "price_current",
        "category",
        "created_at",
        "updated_at",
    )
    list_filter = list_display


class CountryAdmin(BaseModelAdmin):
    list_display = ("name", "code", "phone_code")
    list_filter = list_display


class ShippingAddressAdmin(BaseModelAdmin):
    list_display = ("user", "full_name", "email")
    list_filter = list_display + ("state", "country")


class CouponAdmin(BaseModelAdmin):
    list_display = ("code", "percentage_off", "expiry_date")
    list_filter = list_display
    readonly_fields = ("code", "created_at")


class OrderAdmin(BaseModelAdmin):
    readonly_fields = ("tx_ref",)
    list_display = (
        "user",
        "tx_ref",
        "delivery_status",
        "payment_status",
        "date_delivered",
        "created_at",
    )
    list_filter = list_display


class OrderItemAdmin(BaseModelAdmin):
    list_display = ("user", "guest", "product", "quantity", "created_at")
    list_filter = list_display


class ReviewAdmin(BaseModelAdmin):
    list_display = ("user", "product", "rating", "created_at", "updated_at")
    list_filter = list_display


admin.site.register(Size, SizeAdmin)
admin.site.register(Color, SizeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
