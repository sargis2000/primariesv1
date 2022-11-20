from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CandidatePost, CandidateProfile
from accounts.serializers import CandidatePostSerializer, CandidateProfileSerializer
from accounts.utils import CandidatePermission, VoterPermission
from accounts.views import send_mailgun_mail
from .models import MarkModel, News
from .serializers import *

__all__ = [
    "MarkCandidateAPIView",
    "EvaluateAPIView",
    "NewsAPIView",
    "GetCandidateProfiles",
    "GetCandidateByID",
    "SendMailAPIVIEW"
]


class MarkCandidateAPIView(APIView):
    """This class is a subclass of the APIView class, and it's purpose is to mark a candidate as hired."""
    permission_classes = [
        permissions.IsAuthenticated,
        VoterPermission | CandidatePermission,
    ]

    def get(self, request) -> Response:
        """
        It takes a request, gets all the MarkModel objects, serializes them, and returns them in a response

        :param request: The request object
        :return: A list of all the marks in the database.
        """

        choice_queryset = MarkModel.objects.all()
        serializer = MarkModelSerializer(instance=choice_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EvaluateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request) -> Response:
        """
        The function takes a request object, and returns a response object

        :param request: The request object
        :return: The serializer.data is being returned.
        """
        request.data["voter"] = request.user.voterprofile.id
        serializer = EvaluateModelSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewsAPIView(APIView):
    """Class which returns news objects in order by creation date"""

    def get(self, request):
        """
        It gets the id from the query params, if it exists, and if it does, it tries to get the news by id, and if it
        doesn't exist, it returns a response saying that the news does not exist, and if it does exist, it returns the
        serialized data

        :param request: The request object is the first parameter to any view. It contains all the information about the
        request that was made to the server
        :return: A list of all the news objects in the database.
        """
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
        """
        It returns a list of all candidate profiles

        :param request: The request object
        :return: A list of all the candidate profiles.
        """
        response = CandidateProfile.objects.filter(user__is_candidate=True)
        serializer = CandidateProfilesSerializer(instance=response, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetCandidateByID(APIView):
    permission_classes = (IsAuthenticated, VoterPermission)

    def get(self, request):
        """
        It gets a candidate profile and then gets all the posts associated with that profile and returns them in a response

        :param request: The request object
        :return: The candidate profile and the candidate posts
        """
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


class SendMailAPIVIEW(APIView):
    """# This class is a subclass of the APIView class, and it's purpose is to send an email to the user."""
    permission_classes = (IsAuthenticated,)
    """
    It takes a POST request with a candidate_id, full_name, email, and message, and sends an email to the candidate's
    email address
    
    :param request: The request object
    :return: The response is a string.
    """

    def post(self, request):
        data = self.request.data
        full_name = data['full_name']
        from_mail = data['email']
        message = data['message']
        try:
            to_mail = CandidateProfile.objects.get(id=data['candidate_id'])
        except CandidateProfile.DoesNotExist:
            return Response(
                "Candidate profile does not exist", status=status.HTTP_400_BAD_REQUEST
            )
        else:
            message += f'\n\nՀարգանքներով {full_name}'
            try:
                send_mailgun_mail(form=from_mail,
                                  to=to_mail,
                                  subject=None,
                                  message=message)
            except:
                return Response("email not sent.", status=status.HTTP_400_BAD_REQUEST)
            return Response("email sent successful", status=status.HTTP_200_OK)
