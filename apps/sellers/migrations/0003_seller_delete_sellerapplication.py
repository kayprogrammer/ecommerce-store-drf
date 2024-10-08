# Generated by Django 5.0.7 on 2024-09-07 05:19

import autoslug.fields
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sellers", "0002_sellerapplication_slug"),
        ("shop", "0004_remove_order_shipping_address_order_address_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Seller",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("full_name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254)),
                ("phone_number", models.CharField(max_length=20)),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                ("business_name", models.CharField(max_length=255)),
                (
                    "slug",
                    autoslug.fields.AutoSlugField(
                        always_update=True,
                        editable=False,
                        null=True,
                        populate_from="business_name",
                    ),
                ),
                (
                    "business_type",
                    models.CharField(
                        choices=[
                            ("sole_proprietorship", "Sole Proprietorship"),
                            ("llc", "Limited Liability Company (LLC)"),
                            ("corporation", "Corporation"),
                            ("partnership", "Partnership"),
                        ],
                        max_length=50,
                    ),
                ),
                ("business_registration_number", models.CharField(max_length=50)),
                ("tax_identification_number", models.CharField(max_length=50)),
                ("website_url", models.URLField(blank=True, null=True)),
                ("business_description", models.TextField()),
                ("business_address", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=100)),
                ("state_province", models.CharField(max_length=100)),
                ("postal_code", models.CharField(max_length=20)),
                ("bank_name", models.CharField(max_length=255)),
                ("bank_account_number", models.CharField(max_length=50)),
                ("bank_routing_number", models.CharField(max_length=50)),
                ("account_holder_name", models.CharField(max_length=255)),
                (
                    "government_id",
                    models.FileField(upload_to="sellers/government_ids/"),
                ),
                (
                    "proof_of_address",
                    models.FileField(upload_to="sellers/proof_of_address/"),
                ),
                (
                    "business_license",
                    models.FileField(
                        blank=True, null=True, upload_to="sellers/business_licenses/"
                    ),
                ),
                ("expected_sales_volume", models.CharField(max_length=50)),
                (
                    "preferred_shipping_method",
                    models.CharField(
                        choices=[
                            ("standard", "Standard"),
                            ("expedited", "Expedited"),
                            ("overnight", "Overnight"),
                        ],
                        max_length=20,
                    ),
                ),
                ("additional_comments", models.TextField(blank=True, null=True)),
                ("agree_to_terms", models.BooleanField(default=False)),
                ("is_approved", models.BooleanField(default=False)),
                (
                    "country",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="shop.country",
                    ),
                ),
                ("product_categories", models.ManyToManyField(to="shop.category")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seller",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.DeleteModel(
            name="SellerApplication",
        ),
    ]
