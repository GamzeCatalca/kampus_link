
from rest_framework.permissions import BasePermission


class CanCreateEvent(BasePermission):

    message = "Only club representatives and admins can create events."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["CLUB_REP", "ADMIN"]
        )


class CanManageEvent(BasePermission):

    message = "You can only manage events belonging to your own club."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ["CLUB_REP", "ADMIN"]
        )

    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMIN":
            return True

        if request.user.role == "CLUB_REP":
            return obj.club.representative_id == request.user.id

        return False
