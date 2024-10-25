from apps.common.exceptions import ValidationErr
from apps.shop.models import Category, Color, Size
from asgiref.sync import sync_to_async


async def validate_category_sizes_colors(data):
    # Validate category, sizes and colors
    category_slug = data.pop("category_slug", None)
    category = None
    if category_slug:
        category = await Category.objects.aget_or_none(slug=category_slug)
        if not category:
            raise ValidationErr("category_slug", "Invalid category")
        data["category"] = category
    sizes = data.pop("sizes", [])
    sizes = [s for s in sizes if s != ""]
    if len(sizes) > 0:
        sizes = await sync_to_async(list)(Size.objects.filter(value__in=sizes))
        if len(sizes) < 1:
            raise ValidationErr("sizes", "Enter at least one valid size")
    colors = data.pop("colors", [])
    colors = [c for c in colors if c != ""]
    if len(colors) > 0:
        colors = await sync_to_async(list)(Color.objects.filter(value__in=colors))
        if len(colors) < 1:
            raise ValidationErr("colors", "Enter at least one valid color")
    return data, sizes, colors
