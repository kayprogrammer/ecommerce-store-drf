# Generated by Django 5.0.7 on 2024-08-06 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_remove_category_is_deleted_remove_color_is_deleted_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
