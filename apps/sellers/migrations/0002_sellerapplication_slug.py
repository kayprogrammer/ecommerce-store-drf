# Generated by Django 5.0.7 on 2024-09-07 04:40

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sellers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sellerapplication",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                always_update=True,
                editable=False,
                null=True,
                populate_from="business_name",
            ),
        ),
    ]
