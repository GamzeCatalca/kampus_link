from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):

    message = "Only students can register for events."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "STUDENT"
        )