
from django.db import IntegrityError
from django.db.models import Sum
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import EvaluateModel, GlobalConfigs
from accounts.models import CandidatePost, CandidateProfile, VoterProfile
from accounts.serializers import CandidatePostSerializer, CandidateProfileSerializer
from accounts.utils import CandidatePermission, VoterPermission
from accounts.views import send_mailgun_mail
from .models import MarkModel, News, VotingModel
from .serializers import *
from django.conf import settings
from rest_framework.serializers import ValidationError

__all__ = [
    "MarkCandidateAPIView",
    "EvaluateAPIView",
    "NewsAPIView",
    "GetCandidateProfiles",
    "GetCandidateByID",
    "SendMailAPIVIEW",
    "GetEvaluateResult",
    "VoteView",
]

def has_dublicates(votes: list) -> bool:

    for i in votes:
        if votes.count(i) > 1:
            return True
    return False


def valid_ids(votes: list) -> bool:
    candidate_ids = [str(i.id) for i in CandidateProfile.objects.all()]
    for id in votes:
        if id not in candidate_ids:
            return False
    return True


class MarkCandidateAPIView(APIView):
    """This class is a subclass of the APIView class, and it's purpose is to mark a candidate as hired."""

    permission_classes = [permissions.IsAuthenticated, VoterPermission]

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
    permission_classes = [permissions.IsAuthenticated, VoterPermission]

    def get(self, request):
        candidate_id = request.query_params.get("candidate", None)
        if candidate_id:
            try:
                voter_profile = VoterProfile.objects.get(user_id=request.user.id)
                try:
                    result = EvaluateModel.objects.get(
                        voter_id=voter_profile.id, candidate_id=candidate_id
                    )
                except EvaluateModel.DoesNotExist:
                    result = None
                serializer = EvaluateModelSerializer(instance=result)
            except VoterProfile.DoesNotExist:
                raise ValidationError(
                    "Ընտրողի Սխալ. էջը գոյություն չունի!, Նախ ստեղծեք  Ընտրողի էջ․"
                )

            if result:
                # if serializer.is_valid():
                return Response(
                    {"voted": True, "model": serializer.data}, status=status.HTTP_200_OK
                )
                # return Response({'voted': True, 'model': serializer.errors}, status=status.HTTP_200_OK)
            return Response({"voted": False}, status=status.HTTP_200_OK)
        else:
            raise ValidationError("Թեկնածուի ID-ն բացակայում է")

    def post(self, request) -> Response:
        """
        The function takes a request object, and returns a response object

        :param request: The request object
        :return: The serializer.data is being returned.
        """
        try:
            request.data["voter"] = VoterProfile.objects.get(user_id=request.user.id).id
        except VoterProfile.DoesNotExist:
            raise ValidationError(
                "Ընտրողի Սխալ. էջը գոյություն չունի!, Նախ ստեղծեք  Ընտրողի էջ․"
            )

        try:
            exist = EvaluateModel.objects.filter(
                voter_id=request.data["voter"], candidate_id=request.data["candidate"]
            ).first()
        except EvaluateModel.DoesNotExist:
            exist = None
        if exist:
            exist.poll = MarkModel.objects.get(id=request.data["poll"])
            exist.save()
            serializer = EvaluateModelSerializer(data=request.data, instance=exist)
            if serializer.is_valid():
                return Response(
                    {"data_updated": serializer.data}, status=status.HTTP_200_OK
                )
            else:
                return Response(serializer.errors, status=status.HTTP_200_OK)
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
    """This class is a subclass of the APIView class, and it's purpose is to send an email to the user."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        It takes a request, gets the data from the request, gets the candidate profile from the database, sends an email to
        the candidate, and returns a response

        :param request: The request object
        :return: The response is a string.
        """
        data = self.request.data
        full_name = data["full_name"]
        from_mail = data["email"]
        message = data["message"]
        admin = data.get("admin", None)
        try:
            candidate = CandidateProfile.objects.get(id=data["candidate_id"])
            to_mail = candidate.email
            if admin is not None:
                to_mail = settings.ADMIN_EMAIL
        except CandidateProfile.DoesNotExist:
            return Response(
                "Candidate profile does not exist", status=status.HTTP_400_BAD_REQUEST
            )
        else:
            message += f"\n\nՀարգանքներով {full_name}"
            res = send_mailgun_mail(
                form=from_mail, to=to_mail, subject=None, message=message
            )

            if res.status_code != 200:
                return Response(f"email not sent.", status=status.HTTP_400_BAD_REQUEST)
            return Response(f"email sent successful", status=status.HTTP_200_OK)


class GetEvaluateResult(APIView):
    def get(self, request):
        candidate_id = request.query_params.get("candidate", None)
        if candidate_id:
            try:
                candidate_profile = CandidateProfile.objects.get(id=candidate_id)
            except CandidateProfile.DoesNotExist:
                return Response(
                    "Նշված ID-ով Թեկնածու գոյություն չունի",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                if not candidate_profile.user.is_candidate:
                    return Response(
                        "Նշված ID-ով Թեկնածուն հասանելի չէ",
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                queryset = EvaluateModel.objects.filter(candidate=candidate_profile)
                res = sum([i.poll.mark for i in queryset])
                return Response({"points": res})

        else:
            res = (
                EvaluateModel.objects.values("candidate")
                .order_by("candidate")
                .annotate(points=Sum("poll__mark"))
            )
            return Response(res, status.HTTP_200_OK)


class VoteView(APIView):
    permission_classes = (permissions.IsAuthenticated, VoterPermission)

    def post(self, request):

        votes = request.data.getlist("votes", None)
        stage = GlobalConfigs.objects.get(id=1).stage
        try:
            voter_profile = VoterProfile.objects.get(user=request.user)
        except VoterProfile.DoesNotExist:
            return Response("Ընտրողի տվյալների սխալ")

        if votes is None:
            return Response(
                "ընտրության տվյալները դատարկ են", status=status.HTTP_400_BAD_REQUEST
            )

        if has_dublicates(votes):
            return Response("Սխալ քվեաթերթիկ", status=status.HTTP_400_BAD_REQUEST)
        if not valid_ids(votes):
            return Response("Թեկնածուների ID-ների Սխալ")

        if VotingModel.objects.filter(voter=voter_profile, stage=stage).exists():
            return Response("Ընտրողը արդեն քվերկել է", status=status.HTTP_400_BAD_REQUEST)

        for i, j in enumerate(votes, start=1):
            if i > CandidateProfile.objects.all().count():
                return Response("Ընտրության համարի սԽալ", status=status.HTTP_400_BAD_REQUEST)
            try:
                VotingModel.objects.create(
                    voter=voter_profile,
                    candidate=CandidateProfile.objects.get(id=j),
                    position=i,
                    stage=stage
                )
            except CandidateProfile.DoesNotExist:
                return Response(f"Նշված ID ով թեկնածու գոյություն չունի id={j}", status=status.HTTP_400_BAD_REQUEST)
        return Response("OK", status.HTTP_200_OK)
