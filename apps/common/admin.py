from typing import Any
from django.contrib import admin
from django.http import HttpRequest
from django.utils.safestring import mark_safe

# To ensure that the admin header is bold
admin.site.site_header = mark_safe(
    '<strong style="font-weight:bold;">E-STORE ADMIN</strong>'
)


class BaseModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return self.model.objects.unfiltered()

    def delete_model(self, request: HttpRequest, obj: Any) -> None:
        obj.hard_delete()

    def delete_queryset(self, request, queryset):
        queryset.delete(hard_delete=True)
