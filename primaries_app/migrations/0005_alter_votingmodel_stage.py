# Generated by Django 4.1.1 on 2022-12-21 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("primaries_app", "0004_alter_votingmodel_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="votingmodel",
            name="stage",
            field=models.IntegerField(default=None),
        ),
    ]
