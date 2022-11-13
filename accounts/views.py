import requests
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import authentication, permissions, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from .models import CandidatePost, CandidateProfile, User, VoterProfile
from .serializers import *
from .utils import CandidatePermission, VoterPermission


__all__ = (
    "GetCSRFToken",
    "UserApiView",
    "VoterProfileConfirmMail",
    "VoterProfileAPIView",
    "ActivateVoterProfileAPIView",
    "CandidateProfileConfirmMail",
    "CandidateProfileAPIview",
    "ActivateCandidateProfileAPIView",
    "CandidatePostAPIView",
    "LoginAPIView",
    "LogoutAPIView",
    "FacebookLogin",
    "SessionView",
)


def csrf_failure(request, reason=""):
    return Response(
        {"message": "csrf missing  or incorrect"}, status=status.HTTP_400_BAD_REQUEST
    )


def send_mailgun_mail(form: str, to: list, subject: str, message: str) -> Response:
    result = requests.post(
        "https://api.mailgun.net/v3/primaries.am/messages",
        auth=("api", settings.EMAIL_HOST_PASSWORD),
        data={"from": form, "to": to, "subject": subject, "text": message},
    )
    print(result)
    return result


def get_user(request):
    """Getting Current user and the token.

    :param request: request object
    :return user, confirmation_token:
    """
    user_id = request.GET.get("user_id", "")
    confirmation_token = request.GET.get("confirmation_token", "")
    try:
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    return user, confirmation_token


def create_confirmation_url(user: User, activation_url: str) -> str:
    """
    creates and returns confirmation url for current user

    :param user:
    :param activation_url:
    :return confirm_url:
    """
    token = default_token_generator.make_token(user)
    confirm_url = f"{activation_url}?user_id={user.id}&confirmation_token={token}"
    return confirm_url


class AnonThrottle(AnonRateThrottle):
    rate = "1/s"

    def parse_rate(self, rate):
        """rate parser"""
        return 5, 600


class UserThrottle(UserRateThrottle):
    rate = "1/s"

    def parse_rate(self, rate):
        """rate parser"""
        return 5, 600


class GetCSRFToken(APIView):
    """
    A class which sets CSRF token cookie
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request) -> Response:
        """
        :param request:
        :return Response:
        """
        x = get_token(request)
        res = Response(
            {"success": "CSRF cookie set", "scrftoken": x},
            status=status.HTTP_201_CREATED,
        )
        res.set_cookie(key="csrf-token", value=x)
        return res


class SessionView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        # check voter
        try:
            voter_profile = VoterProfile.objects.get(user=request.user)
        except VoterProfile.DoesNotExist:
            voter_status = ""
        else:
            if voter_profile.user.is_voter:
                voter_status = "active"
            else:
                voter_status = "pending"
        # check candidate
        try:
            candidate_profile = CandidateProfile.objects.get(user=request.user)
        except CandidateProfile.DoesNotExist:
            candidate_status = ""
        else:
            if candidate_profile.user.is_candidate:
                candidate_status = "active"
            else:
                candidate_status = "pending"
        return Response(
            {
                "isAuthenticated": True,
                "voter_status": voter_status,
                "candidate_status": candidate_status,
            }
        )


@method_decorator(csrf_protect, "post")
class UserApiView(APIView):

    """A class which creates User object"""

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.AllowAny]

    # throttle_classes = (AnonThrottle, UserThrottle,)

    def post(self, request) -> Response:
        """

        :param request:
        :return Response: serializer data if success otherwise serializer errors
        """
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VoterProfileConfirmMail(APIView):
    """A class which send email when voter creates profile or requests new one"""

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # throttle_classes = (AnonThrottle, UserThrottle,)

    def get(self, request) -> Response:
        """

        :param request: request object
        :return Response: status 200 if success otherwise status 400
        """
        try:
            send_mailgun_mail(
                form=settings.EMAIL_FROM,
                to=[request.user.voterprofile.email],
                subject="Confirmation mail",
                message="please click  below link to confirm voter profile. "
                "If isn't it you, you can easy delete or ignor this mail\n"
                + create_confirmation_url(
                    request.user, activation_url=settings.VOTER_PROFILE_ACTIVATION_URL
                ),
            )
        except:
            return Response("email not sent", status=status.HTTP_400_BAD_REQUEST)
        return Response("email sent successful", status=status.HTTP_200_OK)


@method_decorator(csrf_protect, "put")
@method_decorator(csrf_protect, "post")
class VoterProfileAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    """
    A class which get, create and update Voter profile

        get: get voter profile objects
        post: creates voter profile object
        put: updates voter profile object
    """

    def get(self, request) -> Response:
        """

        :param request: request object
        :return Response: serializer data if user object exist otherwise status 404
        """
        try:
            voter_profile = VoterProfile.objects.get(user=request.user)
            serializer = VoterProfileSerializer(voter_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except VoterProfile.DoesNotExist:
            return Response(
                "profile object does not exists", status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request) -> Response:
        """

        :param request: request object
        :return Response: serializer data if success otherwise serializer errors
        """
        request.data["user"] = request.user.pk
        serializer = VoterProfileSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            try:
                sender = VoterProfileConfirmMail()
                sender.get(request=request)
            except:
                message = {
                    [
                        "message"
                    ]: "Email don't sent please request another confirmation email"
                }
                return Response(message, status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
            updates Voter profile
        :param request: request object
        :param args: unnamed arguments
        :param kwargs: named arguments
        :return Response: serializer data if success otherwise serializer errors
        """
        try:
            instance = VoterProfile.objects.get(user=request.user)
        except VoterProfile.DoesNotExist:
            return Response(
                "Voter doe not exists firs of all create profile",
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = VoterProfileSerializer(
            data=request.data, instance=instance, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateVoterProfileAPIView(APIView):
    """
    A class which activates voter profile
    """

    authentication_classes = [SessionAuthentication]

    # throttle_classes = (AnonThrottle, UserThrottle,)

    def get(self, request, pk=None) -> Response:
        """

        :param request:
        :param pk:
        :return Response: message with status
        """
        user, confirmation_token = get_user(request)
        if user is None:
            return Response(
                {"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST
            )
        if user.voterprofile.is_email_verified is True:
            return Response(
                {"message": "Voter profile already activated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, confirmation_token):
            return Response(
                {
                    "message": "Token is invalid or expired. Please request another confirmation email by signing in."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.voterprofile.is_email_verified = True
        user.is_voter = True
        user.save()
        user.voterprofile.save()
        return Response({"message": "Email successfully confirmed"}, status.HTTP_200_OK)


class CandidateProfileConfirmMail(APIView):
    """A class which sent email for confirmation Candidate profile"""

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # throttle_classes = (AnonThrottle, UserThrottle,)

    def get(self, request) -> Response:
        try:
            send_mailgun_mail(
                form=settings.EMAIL_FROM,
                to=[request.user.candidateprofile.email],
                subject="Confirmation mail",
                message="please click  below link to confirm candidate profile "
                "and wait till admin accept your profile.\n "
                "If isn't it you, you can easy delete or ignor this mail\n"
                + create_confirmation_url(
                    request.user,
                    activation_url=settings.CANDIDATE_PROFILE_ACTIVATION_URL,
                ),
            )
        except:
            return Response("email not sent")
        return Response("email sent successful")


@method_decorator(csrf_protect, "post")
@method_decorator(csrf_protect, "put")
class CandidateProfileAPIview(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    """A class which creat, update and get profiles
    get: get profile list
    post: create profile
    put: update profile
    """

    def get(self, request) -> Response:
        try:
            profile = CandidateProfile.objects.get(user=request.user)
        except CandidateProfile.DoesNotExist:
            return Response("User does not exist", status=status.HTTP_404_NOT_FOUND)
        serializer = CandidateProfileSerializer(instance=profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request) -> Response:
        """

        :param request:
        :return: serializer data if success otherwise serializer errors
        """
        request.data["user"] = request.user.pk
        serializer = CandidateProfileSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            try:
                sender = CandidateProfileConfirmMail()
                sender.get(request=request)
            except:
                message = {
                    [
                        "message"
                    ]: "Email don't sent please request another confirmation email"
                }
                return Response(message, status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """

        :param request:
        :param args: unnamed arguments
        :param kwargs: named arguments
        :return: serializer data if success otherwise serializer errors
        """
        try:

            instance = CandidateProfile.objects.get(user=request.user)
        except CandidateProfile.DoesNotExist:
            return Response(
                "Candidate does not exists firs of all create profile",
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CandidateProfileSerializer(
            data=request.data, instance=instance, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateCandidateProfileAPIView(APIView):
    """
    class which activates candidate profile
    """

    authentication_classes = [SessionAuthentication]

    # throttle_classes = (AnonThrottle, UserThrottle,)

    def get(self, request, pk=None):
        """

        :param request:
        :param pk:
        :return Response:
        """

        user, confirmation_token = get_user(request)
        if user is None:
            return Response(
                {"message": "User not found"}, status=status.HTTP_400_BAD_REQUEST
            )
        if user.candidateprofile.is_email_verified is True:
            return Response(
                {"message": "Candidate profile already activated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, confirmation_token):
            return Response(
                {
                    "message": "Token is invalid or expired. Please request another confirmation email by signing in."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.candidateprofile.is_email_verified = True
        user.candidateprofile.save()
        try:
            send_mail(
                subject="Candidate verified email",
                message=f"pls check Candidate profiles. {request.user} created profile and verified email",
                from_email=settings.EMAIL_FROM,
                recipient_list=(settings.ADMIN_EMAIL,),
            )
        except:
            return Response("Raised error")
        return Response({"message": "Email successfully confirmed"}, status.HTTP_200_OK)


@method_decorator(csrf_protect, "post")
@method_decorator(csrf_protect, "put")
class CandidatePostAPIView(APIView):
    """A class which creates and updates candidate posts"""

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated, CandidatePermission]

    def get(self, request) -> Response:
        posts = CandidatePost.objects.filter(profile=request.user.candidateprofile)
        serializer = CandidatePostSerializer(instance=posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """

        :param request: request object
        :return: serializer data if success otherwise serializer errors
        """
        request.data["profile"] = request.user.candidateprofile.pk
        serializer = CandidatePostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs) -> Response:
        """

        :param request: request object
        :param args: named arguments
        :param kwargs: unnamed arguments
        :return Response:
        """
        try:
            instance = CandidatePost.objects.get(user=request.user)
        except VoterProfile.DoesNotExist:
            return Response(
                "Post does not exists firs of all create profile",
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CandidatePostSerializer(
            data=request.data, instance=instance, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_protect, "post")
class LoginAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = (permissions.AllowAny,)

    # throttle_classes = (AnonThrottle, UserThrottle,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            login(request, user)
            return Response(user.username, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    authentication_classes = [authentication.SessionAuthentication]

    def get(self, request):
        logout(request)
        return Response("user logout", status=status.HTTP_200_OK)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
