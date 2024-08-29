from django.contrib import admin

from apps.common.admin import BaseModelAdmin
from .models import SellerApplication

# Register your models here.


class SellerApplicationAdmin(BaseModelAdmin):
    list_display = ("user", "full_name", "business_name")
    list_filter = list_display


admin.site.register(SellerApplication, SellerApplicationAdmin)
