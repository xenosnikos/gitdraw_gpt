# Generated by Django 4.2 on 2023-04-13 08:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Repository",
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
                ("name", models.CharField(max_length=100)),
                ("url", models.URLField()),
                ("last_synced", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="File",
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
                ("name", models.CharField(max_length=255)),
                ("path", models.CharField(max_length=255)),
                ("content", models.TextField()),
                (
                    "repository",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="repo_sync.repository",
                    ),
                ),
            ],
        ),
    ]
