
from rest_framework import serializers
from .models import Registration


class RegistrationSerializer(serializers.ModelSerializer):

    event_title = serializers.CharField(
        source="event.title",
        read_only=True,
    )

    student_username = serializers.CharField(
        source="student.username",
        read_only=True,
    )

    class Meta:
        model = Registration

        fields = (
            "id",
            "student",
            "student_username",
            "event",
            "event_title",
            "status",
            "registered_at",
        )

        read_only_fields = (
            "id",
            "student",
            "student_username",
            "status",
            "registered_at",
        )
class RegistrationCancelResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    cancelled_registration_id = serializers.IntegerField()
    promoted_student = serializers.CharField(allow_null=True)