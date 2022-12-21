# Generated by Django 4.1.1 on 2022-12-21 06:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_voterprofile_votes_count_alter_voterprofile_is_paid"),
        ("primaries_app", "0002_votingmodel"),
    ]

    operations = [
        migrations.AlterField(
            model_name="votingmodel",
            name="candidate",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="accounts.candidateprofile",
            ),
        ),
        migrations.AlterField(
            model_name="votingmodel",
            name="voter",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="accounts.voterprofile"
            ),
        ),
    ]