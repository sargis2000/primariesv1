from django.shortcuts import render
from rest_framework import permissions
from .models import PayForEvaluate
from .serializers import PayForEvaluateSerializer
from accounts.models import VoterProfile

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status


class IdramPayForEvaluate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            voter_profile = VoterProfile.objects.get(user_id=request.user.id)
        except VoterProfile.DoesNotExist:
            return Response("Օգտատերը ընտրողի էջ չունի", status.HTTP_400_BAD_REQUEST)
        else:
            if voter_profile.is_paid:
                return Response(
                    "Օգտատերը արդեն վճարել է գնահատման համար",
                    status.HTTP_400_BAD_REQUEST,
                )
            data = PayForEvaluate.objects.get_or_create(profile=voter_profile)
            serializer = PayForEvaluateSerializer(data[0])
            return Response(serializer.data, status=status.HTTP_200_OK)


class PayForVoting(APIView):
    def get(self, request):
        try:
            voter_profile = VoterProfile.objects.get(user_id=request.user.id)
        except VoterProfile.DoesNotExist:
            return Response("Օգտատերը ընտրողի էջ չունի", status.HTTP_400_BAD_REQUEST)
        else:
            if not voter_profile.is_paid:
                return Response(
                    "Օգտատերը չի վճարել է գնահատման համար, նախ պետք է վճարել գնահատման համար ընտրողի կարգավիճակ ստանալու համար",
                    status.HTTP_400_BAD_REQUEST,
                )
            pass

