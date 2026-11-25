from rest_framework import serializers

from clubs.models import Club
from registrations.models import Registration
from .models import Event


class EventSerializer(serializers.ModelSerializer):

    club_name = serializers.CharField(
        source="club.name",
        read_only=True,
    )

    university_name = serializers.CharField(
        source="club.university.name",
        read_only=True,
    )

    registered_count = serializers.SerializerMethodField()
    remaining_capacity = serializers.SerializerMethodField()
    my_registration_status = serializers.SerializerMethodField()

    class Meta:
        model = Event

        fields = (
            "id",
            "title",
            "slug",
            "description",
            "location",
            "start_datetime",
            "end_datetime",
            "registration_deadline",
            "capacity",
            "registered_count",
            "remaining_capacity",
            "cover_image_url",
            "status",
            "club",
            "club_name",
            "university_name",
            "my_registration_status",
        )

    def get_registered_count(self, obj) -> int:
        return Registration.objects.filter(
            event=obj,
            status=Registration.Status.REGISTERED,
        ).count()

    def get_remaining_capacity(self, obj) -> int | None:
        if obj.capacity is None:
            return None

        registered_count = self.get_registered_count(obj)

        return max(obj.capacity - registered_count, 0)

    def get_my_registration_status(self, obj) -> str | None:
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return None

        registration = Registration.objects.filter(
            event=obj,
            student=request.user,
        ).first()

        if registration:
            return registration.status

        return None


class EventCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event

        fields = (
            "id",
            "club",
            "title",
            "description",
            "location",
            "start_datetime",
            "end_datetime",
            "registration_deadline",
            "capacity",
            "cover_image_url",
        )

        read_only_fields = ("id",)

    def validate_club(self, club):
        user = self.context["request"].user

        if club.status != Club.Status.APPROVED:
            raise serializers.ValidationError(
                "Only approved clubs can have events created."
            )

        if (
            user.role == "CLUB_REP"
            and club.representative_id != user.id
        ):
            raise serializers.ValidationError(
                "You can only create events for your own club."
            )

        return club

    def validate(self, attrs):

        start_datetime = attrs.get(
            "start_datetime",
            getattr(self.instance, "start_datetime", None),
        )

        end_datetime = attrs.get(
            "end_datetime",
            getattr(self.instance, "end_datetime", None),
        )

        registration_deadline = attrs.get(
            "registration_deadline",
            getattr(self.instance, "registration_deadline", None),
        )

        if start_datetime and end_datetime and end_datetime <= start_datetime:
            raise serializers.ValidationError({
                "end_datetime": "End time must be after start time."
            })

        if (
            registration_deadline
            and start_datetime
            and registration_deadline > start_datetime
        ):
            raise serializers.ValidationError({
                "registration_deadline": (
                    "Registration deadline cannot be after the event starts."
                )
            })

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user

        return Event.objects.create(
            **validated_data,
            created_by=user,
            status=Event.Status.DRAFT,
        )