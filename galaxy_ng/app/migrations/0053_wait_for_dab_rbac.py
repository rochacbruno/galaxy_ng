# Generated by Django 4.2.10 on 2024-02-15 17:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("galaxy", "0052_alter_organization_created_by_and_more"),
    ]

    run_before = [
        ("dab_rbac", "__first__")
    ]
