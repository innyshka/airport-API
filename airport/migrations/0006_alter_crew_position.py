# Generated by Django 4.2.6 on 2023-10-20 13:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("airport", "0005_jobposition_crew_position"),
    ]

    operations = [
        migrations.AlterField(
            model_name="crew",
            name="position",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="crews",
                to="airport.jobposition",
            ),
        ),
    ]
