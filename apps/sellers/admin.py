from django.contrib import admin

from apps.common.admin import BaseModelAdmin
from .models import Seller

# Register your models here.


class SellerAdmin(BaseModelAdmin):
    list_display = ("user", "full_name", "business_name")
    list_filter = list_display

    readonly_fields = ("slug",)


admin.site.register(Seller, SellerAdmin)
