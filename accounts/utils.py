from rest_framework import permissions
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled


class CandidatePermission(permissions.BasePermission):
    """class which check candidate permission"""

    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS or request.user.is_candidate:
            return True


class VoterPermission(permissions.BasePermission):
    """class which check voter permission"""

    def has_permission(self, request, view) -> bool:
        if request.method in permissions.SAFE_METHODS or request.user.is_voter:
            return True


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):  # check that a Throttled exception is raised
        time = response.data["detail"].split()[6]
        response.data[
            "detail"
        ] = f"Հարցումն ընդհատվել է : Հասանելի կլինի {time} վայրկյանից:"

    return response
