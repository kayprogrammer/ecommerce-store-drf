# Generated by Django 5.0.7 on 2024-09-07 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0005_alter_product_seller"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="price_old",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
