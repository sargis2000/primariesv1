from rest_framework import serializers
from .models import PayForEvaluate


class PayForEvaluateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayForEvaluate
        exclude = ("id",)