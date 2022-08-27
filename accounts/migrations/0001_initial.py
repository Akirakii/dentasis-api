# Generated by Django 4.1 on 2022-08-20 19:22

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("is_active", models.BooleanField(default=False)),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=datetime.datetime(
                            2022,
                            8,
                            20,
                            19,
                            22,
                            55,
                            928613,
                            tzinfo=datetime.timezone.utc,
                        )
                    ),
                ),
            ],
            options={
                "db_table": "accounts_user",
            },
        ),
        migrations.CreateModel(
            name="UserActivationCode",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("activation_code", models.CharField(max_length=6)),
                (
                    "expire_date",
                    models.DateTimeField(
                        default=datetime.datetime(
                            2022,
                            8,
                            21,
                            19,
                            22,
                            55,
                            928613,
                            tzinfo=datetime.timezone.utc,
                        )
                    ),
                ),
            ],
            options={
                "db_table": "accounts_user_activation_code",
            },
        ),
    ]
