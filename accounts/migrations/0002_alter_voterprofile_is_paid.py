# Generated by Django 4.1.1 on 2022-12-17 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="voterprofile",
            name="is_paid",
            field=models.BooleanField(
                default=False, verbose_name="ՎՃարել է գնահատելու համար"
            ),
        ),
    ]