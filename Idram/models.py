from django.db import models
from accounts.models import VoterProfile
import uuid

# Create your models here.


class PayForEvaluate(models.Model):
    EDP_BILL_NO = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(VoterProfile, on_delete=models.CASCADE, editable=False)
    EDP_AMOUNT = models.CharField(default=1000, editable=False, max_length=100)


