# Generated by Django 5.0.7 on 2024-08-11 23:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0003_order_deleted_at_product_deleted_at"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="shipping_address",
        ),
        migrations.AddField(
            model_name="order",
            name="address",
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="city",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="country",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="email",
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="full_name",
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="phone",
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="state",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="zipcode",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="shippingaddress",
            name="email",
            field=models.EmailField(max_length=254),
        ),
        migrations.AddConstraint(
            model_name="order",
            constraint=models.UniqueConstraint(
                fields=("user", "coupon"), name="unique_user_coupon_order"
            ),
        ),
    ]
