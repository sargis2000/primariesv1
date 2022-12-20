from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from .models import Pay
from .serializers import PaySerializer
from accounts.models import VoterProfile


from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status

# 2000դր - 1 քվե
# 5000դր - 2 քվե
#
# 10000դր - 3քվե
# 20000դր - 4քվե
# 50000դր - 5քվե

values = {1: 2000, 2: 5000, 3: 10000, 4: 20000, 5: 50000}

class PayForEvaluate(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        print(self.request.user)
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
            data = Pay.objects.get_or_create(profile=voter_profile)
            serializer = PaySerializer(data[0])
            return Response(serializer.data, status=status.HTTP_200_OK)


class PayForVoting(APIView):
    def get(self, request):
        count = request.query_params.get("count", None)
        if count is None:
            return Response("Քանակը նշված չէ", status.HTTP_400_BAD_REQUEST)

        if int(count) not in values.keys():
            return Response("Քանակի սխալ", status.HTTP_400_BAD_REQUEST)
        try:
            voter_profile = VoterProfile.objects.get(user_id=request.user.id)
        except VoterProfile.DoesNotExist:
            return Response("Օգտատերը ընտրողի էջ չունի", status.HTTP_400_BAD_REQUEST)
        else:
            if voter_profile.is_paid:
                return Response(
                        "Օգտատերը արդեն վճարել է Քվեառկության համար ",
                        status.HTTP_400_BAD_REQUEST,
                )
            data = Pay.objects.get_or_create(profile=voter_profile, EDP_AMOUNT=count)
            serializer = PaySerializer(data[0])
            return Response(serializer.data, status=status.HTTP_200_OK)



