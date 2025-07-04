# Generated by Django 4.2.20 on 2025-05-09 01:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pgvector.django.vector


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="news_article",
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
                ("title", models.TextField()),
                ("writer", models.TextField()),
                ("write_date", models.DateTimeField()),
                ("category", models.TextField()),
                ("content", models.TextField()),
                ("url", models.TextField(unique=True)),
                ("keywords", models.JSONField(blank=True, null=True)),
                ("embedding", pgvector.django.vector.VectorField(dimensions=1536)),
            ],
            options={
                "db_table": "news_article",
            },
        ),
        migrations.CreateModel(
            name="Reads",
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
                (
                    "article_id",
                    models.ForeignKey(
                        db_column="article_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mynews.news_article",
                        to_field="url",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "read",
            },
        ),
        migrations.CreateModel(
            name="Likes",
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
                (
                    "article_id",
                    models.ForeignKey(
                        db_column="article_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mynews.news_article",
                        to_field="url",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "likes",
                "unique_together": {("user", "article_id")},
            },
        ),
    ]
