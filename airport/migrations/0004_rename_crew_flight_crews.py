# Generated by Django 4.2.6 on 2023-10-20 13:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("airport", "0003_flight_crew"),
    ]

    operations = [
        migrations.RenameField(
            model_name="flight",
            old_name="crew",
            new_name="crews",
        ),
    ]
