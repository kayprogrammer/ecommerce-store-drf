# Generated by Django 5.0.7 on 2024-08-06 21:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_guestuser"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="guestuser",
            name="is_deleted",
        ),
    ]
