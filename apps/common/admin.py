from django.contrib import admin
from django.utils.safestring import mark_safe

# To ensure that the admin header is bold
admin.site.site_header = mark_safe(
    '<strong style="font-weight:bold;">E-STORE ADMIN</strong>'
)
