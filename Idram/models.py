from django.db import models
from accounts.models import VoterProfile
import uuid

# Create your models here.

choice = (
    ("Evaluate", "Գնահատման համար"),
    ("Vote1", "Քվեարկել առաջին անգամ"),
    ("Vote2", "Քվեարկել երկրորդ անգամ"),
    ("Vote3", "Քվեարկել երորդ անգամ"),
    ("Vote4", "Քվեարկել չորորդ անգամ"),
    ("Vote4", "Քվեարկել հինգերորդ անգամ"),
)


class PayForEvaluate(models.Model):
    EDP_BILL_NO = models.UUIDField(
        primary_key=True, default=uuid.uuid4, verbose_name="ՎՃարման ID"
    )
    profile = models.ForeignKey(
        VoterProfile, on_delete=models.CASCADE, verbose_name="Ընտրողի Էջ"
    )
    EDP_AMOUNT = models.IntegerField(default=1000, verbose_name="Գումար")
    EDP_REC_ACCOUNT = models.IntegerField(default=110001952, verbose_name="Ստացողի ID")
    for_what = models.CharField(
        choices=choice, max_length=100, default=choice[0][0], verbose_name="Ինչի համար՞"
    )
    confirmed = models.BooleanField(default=False, verbose_name="Հաստատված է")

    class Meta:
        verbose_name = "ՎՃարումներ"
        verbose_name_plural = "ՎՃարումներ"

    def __str__(self):
        return str(self.EDP_BILL_NO)
