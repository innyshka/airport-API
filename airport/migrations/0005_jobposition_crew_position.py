# Generated by Django 4.2.6 on 2023-10-20 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("airport", "0004_rename_crew_flight_crews"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobPosition",
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
                ("title", models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name="crew",
            name="position",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="crews",
                to="airport.jobposition",
            ),
        ),
    ]
