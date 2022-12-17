from django.shortcuts import render
from rest_framework import permissions
from .models import PayForEvaluate
from .serializers import PayForEvaluateSerializer
from accounts.models import VoterProfile
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView


class IdramPayForEvaluate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            voter_profile = VoterProfile.objects.get(user_id=request.user.id)
        except VoterProfile.DoesNotExist:
            return Response("Օգտատերը ընտրողի էջ չունի")
        else:
            if voter_profile.is_paid:
                return Response("Օգտատերը արդեն վճարել է գնահատման համար")
            data = PayForEvaluate.objects.get_or_create(profile=voter_profile)
            serializer = PayForEvaluateSerializer(instance=data, many=False)
            return Response(serializer.data)

