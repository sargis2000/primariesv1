from accounts.serializers import CandidateProfileSerializer, CandidatePostSerializer
from accounts.utils import VoterPermission, CandidatePermission
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import CandidateProfile
from .models import MarkModel, News
from .serializers import *
from accounts.models import CandidatePost

__all__ = [
    "MarkCandidateAPIView",
    "EvaluateAPIView",
    "NewsAPIView",
    "GetCandidateProfiles",
    "GetCandidateByID",
]


class MarkCandidateAPIView(APIView):
    """
    get:
        Return a list of all the Marking model objects.
    """

    permission_classes = [permissions.IsAuthenticated, VoterPermission | CandidatePermission]

    def get(self, request) -> Response:
        """
        :param request: request object
        :return Response: all MarkModel objects serialized
        """
        choice_queryset = MarkModel.objects.all()
        serializer = MarkModelSerializer(instance=choice_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EvaluateAPIView(APIView):
    """
    post:
        creat EvaluateModel object
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request) -> Response:
        """
        :param request: request object
        :return Response: if serializer valid creates EvaluateModel object otherwise serializer error
        """
        request.data._mutable = True
        request.data["voter"] = request.user.voterprofile.id
        request.data._mutable = False
        serializer = EvaluateModelSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewsAPIView(APIView):
    """Class which returns news objects in order by creation date"""

    def get(self, request):
        id = request.query_params.get("id", None)
        if id is not None:
            try:
                news_by_id = News.objects.get(id=id)
            except News.DoesNotExist:
                return Response(
                    "New does not exist", status=status.HTTP_400_BAD_REQUEST
                )
            else:
                serializer = NewsSerializer(instance=news_by_id)
                return Response(serializer.data, status=status.HTTP_200_OK)
        news = News.objects.all().order_by("created_at")
        serializer = NewsSerializer(instance=news, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetCandidateProfiles(APIView):
    permission_classes = (IsAuthenticated, VoterPermission)

    def get(self, request) -> Response:
        response = CandidateProfile.objects.filter(user__is_candidate=True)
        serializer = CandidateProfilesSerializer(instance=response, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetCandidateByID(APIView):
    permission_classes = (IsAuthenticated, VoterPermission)

    def get(self, request):
        try:
            candidate = CandidateProfile.objects.get(
                id=request.query_params.get("id", None)
            )
        except CandidateProfile.DoesNotExist:
            return Response(
                "Candidate profile does not exist", status=status.HTTP_400_BAD_REQUEST
            )
        else:
            posts = CandidatePost.objects.filter(profile=candidate)
            post_serializer = CandidatePostSerializer(instance=posts, many=True)
            serializer = CandidateProfileSerializer(instance=candidate)
            return Response(
                {"profile": serializer.data, "posts": post_serializer.data},
                status=status.HTTP_200_OK,
            )
