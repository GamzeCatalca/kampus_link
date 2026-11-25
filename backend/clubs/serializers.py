
from rest_framework import serializers

from .models import Club


class ClubSerializer(serializers.ModelSerializer):

    university_name = serializers.CharField(
        source="university.name",
        read_only=True,
    )

    class Meta:
        model = Club

        fields = (
            "id",
            "university",
            "university_name",
            "name",
            "slug",
            "description",
            "logo_url",
            "status",
        )


class ClubCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Club

        fields = (
            "id",
            "university",
            "name",
            "description",
            "logo_url",
        )

        read_only_fields = ("id",)

        validators = []

    def validate_university(self, university):
        if not university.is_active:
            raise serializers.ValidationError(
                "You can only apply to an active university."
            )

        return university
    def validate(self, attrs):
        university = attrs.get("university")
        name = attrs.get("name")

        if university and name:
            existing_club = Club.objects.filter(
                university=university,
                name__iexact=name,
            ).exists()

            if existing_club:
                raise serializers.ValidationError({
                    "name": (
                        "A club with this name already exists "
                        "at this university."
                    )
                })

        return attrs
    def create(self, validated_data):
        user = self.context["request"].user

        return Club.objects.create(
            **validated_data,
            representative=user,
            status=Club.Status.PENDING,
        )
