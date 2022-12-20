from django.db import models
from accounts.models import VoterProfile
import uuid

# Create your models here.


class Pay(models.Model):
    EDP_BILL_NO = models.UUIDField(
        primary_key=True, default=uuid.uuid4, verbose_name="ՎՃարման ID"
    )
    profile = models.ForeignKey(
        VoterProfile, on_delete=models.CASCADE, verbose_name="Ընտրողի Էջ"
    )
    EDP_AMOUNT = models.IntegerField(default=1, verbose_name="Գումար")
    EDP_REC_ACCOUNT = models.IntegerField(default=110001952, verbose_name="Ստացողի ID")
    confirmed = models.BooleanField(default=False, verbose_name="Հաստատված է")

    class Meta:
        verbose_name = "ՎՃարումներ"
        verbose_name_plural = "ՎՃարումներ"

    def __str__(self):
        return str(self.EDP_BILL_NO)
