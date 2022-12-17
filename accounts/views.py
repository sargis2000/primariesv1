import requests
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import authentication, permissions, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from django.contrib import messages
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
    "GetVoterProfiles",
)


def csrf_failure(request, reason=""):
    """It returns a 400 response with a message of "csrf missing or incorrect".

    :param request: The request object
    :param reason: The reason the CSRF check failed. This will be one of REASON_NO_CSRF_COOKIE, REASON_BAD_TOKEN, or
    REASON_MALFORMED_REFERER
    :return: A response object with a message and a status code.
    """
    return Response(
        {"message": "csrf missing  or incorrect"}, status=status.HTTP_400_BAD_REQUEST
    )


def send_mailgun_mail(
    form: str, to: list, subject: str | None, message: str
) -> Response:
    """It sends an email using the Mailgun API.

    :param form: The email address that the email is sent from
    :type form: str
    :param to: The email address of the recipient
    :type to: list
    :param subject: The subject of the email
    :type subject: str
    :param message: The message to be sent
    :type message: str
    :return: The result of the request.
    """
    result = requests.post(
        "https://api.mailgun.net/v3/primaries.am/messages",
        auth=("api", settings.EMAIL_HOST_PASSWORD),
        data={"from": form, "to": to, "subject": subject, "text": message},
    )
    return result


def get_user(request):
    """
    It gets the user from the database, and if it can't find the user, it returns None

    :param request: The request object
    :return: user and confirmation_token
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
    It creates a confirmation URL for a user

    :param user: The user object that you want to send the email to
    :type user: User
    :param activation_url: This is the url that the user will be redirected to after clicking the confirmation link
    :type activation_url: str
    :return: A string
    """

    token = default_token_generator.make_token(user)
    confirm_url = f"{activation_url}?user_id={user.id}&confirmation_token={token}"
    return confirm_url


class AnonThrottle(AnonRateThrottle):
    rate = "1/s"

    def parse_rate(self, rate):
        """
        The function takes in a string, and returns a tuple of two integers
        :param rate: The rate at which the data is sampled
        """

        return 5, 600


class UserThrottle(UserRateThrottle):
    rate = "1/s"

    def parse_rate(self, rate):
        """
        The function takes in a string, and returns a tuple of two integers
        :param rate: The rate at which the data is sampled
        """

        return 5, 600


class GetCSRFToken(APIView):
    """
    A class which sets CSRF token cookie
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request) -> Response:
        """
        It gets the CSRF token from the request, and then sets the CSRF token in the response

        :param request: The request object
        :return: A response object with a cookie and a json object
        """

        x = get_token(request)
        res = Response(
            {"success": "CSRF cookie set", "scrftoken": x},
            status=status.HTTP_201_CREATED,
        )
        res.set_cookie(key="csrf-token", value=x)
        return res


class SessionView(APIView):
    """This class is a subclass of the APIView class, and it's a view that handles the login and logout of users"""

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        """
        It checks if the user is a voter or a candidate, and returns the status of the user

        :param request: The request object
        :param format: The format of the response
        :return: The isAuthenticated key is being returned with a value of True.
        """

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
            candidate_id = ""
        else:
            candidate_id = candidate_profile.id
            if candidate_profile.user.is_candidate:
                candidate_status = "active"
            else:
                candidate_status = "pending"

        return Response(
            {
                "username": request.user.username,
                "isAuthenticated": True,
                "voter_status": voter_status,
                "candidate_id": candidate_id,
                "candidate_status": candidate_status,
            }
        )


@method_decorator(csrf_protect, "post")
class UserApiView(APIView):
    """This class is a subclass of the APIView class, and it's a view that handles HTTP requests for the User model"""

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.AllowAny]

    # throttle_classes = (
    #     AnonThrottle,
    #     UserThrottle,
    # )

    def post(self, request) -> Response:
        """
        If the serializer is valid, save the serializer and return a 201 response. If the serializer is not valid, return a
        400 response

        :param request: The incoming request
        :return: The serializer.data is being returned.
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

    # throttle_classes = (
    #     AnonThrottle,
    #     UserThrottle,
    # )

    def get(self, request) -> Response:
        """
        It sends an email to the user's email address with a link to confirm their voter profile

        :param request: The request object
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
    """This class is a subclass of the APIView class, and it's a view that will return a voter's profile."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request) -> Response:
        """
        It tries to get the voter profile of the user who made the request, and if it exists, it returns the profile data in
        the response

        :param request: The request object is the first parameter to the view. It contains all the information about the
        request that was made to the server
        :return: The voter profile of the user.
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
        It takes a request, creates a serializer, checks if the serializer is valid, saves the serializer, sends an email,
        and returns a response

        :param request: The incoming request
        :return: The serializer.data is being returned.
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
        It tries to get the VoterProfile instance for the current user, if it doesn't exist, it returns a 404 response,
        otherwise it updates the instance with the data from the request and returns a 200 response

        :param request: The request object
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
    """This class is a view that allows a user to activate their voter profile"""

    authentication_classes = [SessionAuthentication]

    # throttle_classes = (
    #     AnonThrottle,
    #     UserThrottle,
    # )

    def get(self, request, pk=None) -> Response:
        """
        The function takes in a request and a primary key (pk) and returns a response

        :param request: The request object
        :param pk: The primary key of the user
        :return: A response object is being returned.
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
    """This class is used to send a confirmation email to the candidate after he/she has successfully created a profile."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # throttle_classes = (
    #     AnonThrottle,
    #     UserThrottle,
    # )

    def get(self, request) -> Response:
        """
        It sends an email to the user's email address with a link to confirm their profile

        :param request: The request object
        :return: The response is a string.
        """
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
    """This class is a subclass of the APIView class, and it's purpose is to provide a view for the candidate profile."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request) -> Response:
        """
        It tries to get the profile of the user who is making the request. If it can't find the profile, it returns a 404
        error. If it can find the profile, it returns the profile's data

        :param request: The request object
        :return: A response object with the serialized data and a status code.
        """
        try:
            profile = CandidateProfile.objects.get(user=request.user)
        except CandidateProfile.DoesNotExist:
            return Response("User does not exist", status=status.HTTP_404_NOT_FOUND)

        serializer = CandidateProfileSerializer(instance=profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request) -> Response:
        """
        It takes a request, creates a serializer with the request data, checks if the serializer is valid, saves the
        serializer, sends an email, and returns a response

        :param request: The request object
        :return: The serializer.data is being returned.
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
        The function is called when a PUT request is made to the endpoint.

        The function first checks if the user has a profile. If not, it returns a 404 error.

        If the user has a profile, it updates the profile with the data in the request.

        If the data is valid, it returns a 200 response with the updated data.

        If the data is invalid, it returns a 400 response with the errors

        :param request: The incoming request
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
    """This class is used to activate a candidate profile"""

    authentication_classes = [SessionAuthentication]

    # throttle_classes = (
    #     AnonThrottle,
    #     UserThrottle,
    # )

    def get(self, request, pk=None):
        """
        It takes a request, gets the user and confirmation token from the request, checks if the user exists, checks if the
        user's email is already verified, checks if the confirmation token is valid, sets the user's email to verified, and
        sends an email to the admin

        :param request: The request object
        :param pk: The primary key of the user
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
    """This class is a subclass of the APIView class, and it's a view that will handle requests to the /api/candidate/<int:pk>/post/ endpoint."""

    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated, CandidatePermission]

    def get(self, request) -> Response:
        """
        It gets all the posts that belong to the user who is making the request

        :param request: The request object
        :return: A list of all the posts that the candidate has made.
        """
        posts = CandidatePost.objects.filter(profile=request.user.candidateprofile)
        serializer = CandidatePostSerializer(instance=posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        It takes a request object, validates the data, saves the data, and returns a response

        :param request: The request object
        :return: The serializer data is being returned if the serializer is valid.
        """
        request.data["profile"] = request.user.candidateprofile.pk
        serializer = CandidatePostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs) -> Response:
        """
        It tries to get the instance of the model from the database, if it doesn't exist, it returns a 404 response, if it
        does exist, it updates the instance with the data from the request and returns a 200 response

        :param request: The incoming request
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
    """This class is a subclass of the APIView class, and it's going to handle the login functionality for our API"""

    authentication_classes = [SessionAuthentication]
    permission_classes = (permissions.AllowAny,)

    # throttle_classes = (
    #     AnonThrottle,
    #     UserThrottle,
    # )

    def post(self, request):
        """
        It takes a request, validates it, logs the user in, and returns a response.

        :param request: The request object
        :return: The username of the user that is logged in.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]
            login(request, user)
            return Response(user.username, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """This class is a subclass of the APIView class, and it's purpose is to logout the user."""

    authentication_classes = [authentication.SessionAuthentication]

    def get(self, request):
        """
        It logs out the user and returns a response with a message and a status code

        :param request: The request object
        :return: The user is being logged out and a response is being returned.
        """
        logout(request)
        return Response("user logout", status=status.HTTP_200_OK)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


def send_email_view(request):
    if request.method == "POST":
        data = request.POST
        message = data["message"]
        mails = data.getlist("mails")
        subject = data["subject"]

        res = send_mailgun_mail(
            form=settings.EMAIL_FROM,
            to=mails,
            subject=subject,
            message=message,
        )
        if res.status_code == 200:
            messages.add_message(
                request, messages.INFO, "էլ․ Հաղորդագրությունները ուղարկված է։"
            )
            return redirect("admin:index")
        else:
            messages.add_message(
                request, messages.WARNING, "էլ․ Հաղորդագրությունները չի ուղարկվել։"
            )
            return redirect("admin:index")


class GetVoterProfiles(APIView):
    """ This class is a subclass of the APIView class, and it has a get method that returns\
             a list of all the voter profiles in the database """

    def get(self, request, *args, **kwargs):
        """A function that gets the request, args, and kwargs.

        :param request: The request object
        """

        voters = VoterProfile.objects.all().filter(user__is_voter=True)
        serializer = VoterProfileSerializer(instance=voters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
