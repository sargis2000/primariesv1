# Generated by Django 4.1.1 on 2022-12-17 14:49

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_voterprofile_is_paid"),
        ("Idram", "0004_remove_payforevaluate_profile_payforevaluate_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="payforevaluate",
            name="confirmed",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="payforevaluate",
            name="EDP_AMOUNT",
            field=models.IntegerField(default=1000),
        ),
        migrations.AlterField(
            model_name="payforevaluate",
            name="EDP_BILL_NO",
            field=models.UUIDField(
                default=uuid.uuid4, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="payforevaluate",
            name="EDP_REC_ACCOUNT",
            field=models.IntegerField(default=110001952),
        ),
        migrations.AlterField(
            model_name="payforevaluate",
            name="for_what",
            field=models.CharField(
                choices=[("Գնահատում", "Գնահատման համար")],
                default="Գնահատում",
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name="payforevaluate",
            name="profile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="accounts.voterprofile"
            ),
        ),
    ]
