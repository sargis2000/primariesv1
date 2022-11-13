from rest_framework import permissions



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
