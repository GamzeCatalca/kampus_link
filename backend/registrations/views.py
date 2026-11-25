
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from events.models import Event
from .models import Registration
from .serializers import RegistrationSerializer
from .permissions import IsStudent
from drf_spectacular.utils import extend_schema
from .serializers import RegistrationSerializer, RegistrationCancelResponseSerializer


class RegistrationCreateView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsStudent]

    def perform_create(self, serializer):

        event_id = self.request.data.get("event")

        with transaction.atomic():

            try:
                event = Event.objects.select_for_update().get(
                    pk=event_id
                )
            except Event.DoesNotExist:
                raise ValidationError({
                    "event": "The selected event does not exist."
                })

            now = timezone.now()

            if event.status != Event.Status.PUBLISHED:
                raise ValidationError(
                    "You can only register for published events."
                )

            if event.start_datetime <= now:
                raise ValidationError(
                    "You cannot register for an event that has already started."
                )

            if (
                event.registration_deadline
                and now > event.registration_deadline
            ):
                raise ValidationError(
                    "The registration deadline has passed."
                )

            existing_registration = (
                Registration.objects.select_for_update()
                .filter(
                    student=self.request.user,
                    event=event,
                )
                .first()
            )

            if (
                existing_registration
                and existing_registration.status != Registration.Status.CANCELLED
            ):
                raise ValidationError(
                    "You are already registered for this event."
                )

            registered_count = Registration.objects.filter(
                event=event,
                status=Registration.Status.REGISTERED,
            ).count()

            if (
                event.capacity is not None
                and registered_count >= event.capacity
            ):
                status = Registration.Status.WAITLISTED
            else:
                status = Registration.Status.REGISTERED

            if existing_registration:
                serializer.instance = existing_registration

                serializer.save(
                    student=self.request.user,
                    status=status,
                    registered_at=now,
                )
            else:
                serializer.save(
                    student=self.request.user,
                    status=status,
                )

class RegistrationCancelView(generics.GenericAPIView):
    serializer_class = RegistrationCancelResponseSerializer
    permission_classes = [IsStudent]

    @extend_schema(
        request=None,
        responses=RegistrationCancelResponseSerializer,
    )
    def post(self, request, pk):
        initial_registration = get_object_or_404(
            Registration,
            pk=pk,
            student=request.user,
        )

        with transaction.atomic():

            event = Event.objects.select_for_update().get(
                pk=initial_registration.event_id
            )

            registration = Registration.objects.select_for_update().get(
                pk=pk,
                student=request.user,
            )

            if registration.status not in [
                Registration.Status.REGISTERED,
                Registration.Status.WAITLISTED,
            ]:
                raise ValidationError(
                    "This registration cannot be cancelled."
                )

            was_registered = (
                registration.status == Registration.Status.REGISTERED
            )

            registration.status = Registration.Status.CANCELLED
            registration.save(update_fields=["status"])

            promoted_student = None

            if was_registered:

                next_registration = (
                    Registration.objects.select_for_update()
                    .filter(
                        event=event,
                        status=Registration.Status.WAITLISTED,
                    )
                    .order_by("registered_at", "id")
                    .first()
                )

                if next_registration:
                    next_registration.status = Registration.Status.REGISTERED
                    next_registration.save(update_fields=["status"])
                    promoted_student = next_registration.student.username

        return Response({
            "message": "Registration cancelled successfully.",
            "cancelled_registration_id": registration.id,
            "promoted_student": promoted_student,
        })


class MyRegistrationsView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return (
            Registration.objects
            .filter(student=self.request.user)
            .select_related("event")
            .order_by("-registered_at")
        )
