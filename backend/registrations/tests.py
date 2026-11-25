
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from universities.models import University
from clubs.models import Club
from events.models import Event
from .models import Registration

User = get_user_model()


class RegistrationAPITests(APITestCase):

    def setUp(self):
        self.university = University.objects.create(
            name="Registration Test University",
        )

        self.student = User.objects.create_user(
            username="registration_student",
            password="StrongPass123!",
            role="STUDENT",
        )

        self.waiting_student = User.objects.create_user(
            username="registration_waiting",
            password="StrongPass123!",
            role="STUDENT",
        )

        self.other_student = User.objects.create_user(
            username="registration_other",
            password="StrongPass123!",
            role="STUDENT",
        )

        self.representative = User.objects.create_user(
            username="registration_rep",
            password="StrongPass123!",
            role="CLUB_REP",
        )

        self.club = Club.objects.create(
            university=self.university,
            name="Registration Test Club",
            representative=self.representative,
            status=Club.Status.APPROVED,
        )

        self.start = timezone.now() + timedelta(days=5)

        self.event = Event.objects.create(
            club=self.club,
            title="Registration Test Event",
            description="A registration test event.",
            location="Istanbul",
            start_datetime=self.start,
            end_datetime=self.start + timedelta(hours=2),
            registration_deadline=self.start - timedelta(days=1),
            capacity=1,
            status=Event.Status.PUBLISHED,
            created_by=self.representative,
        )

        self.client.force_authenticate(user=self.student)

    def test_student_can_register_for_event(self):
        response = self.client.post(
            "/api/registrations/",
            {"event": self.event.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        registration = Registration.objects.get(
            student=self.student,
            event=self.event,
        )

        self.assertEqual(
            registration.status,
            Registration.Status.REGISTERED,
        )

    def test_full_event_places_student_on_waitlist(self):
        Registration.objects.create(
            student=self.student,
            event=self.event,
            status=Registration.Status.REGISTERED,
        )

        response = self.client.post(
            "/api/registrations/",
            {"event": self.event.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.force_authenticate(user=self.waiting_student)

        response = self.client.post(
            "/api/registrations/",
            {"event": self.event.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        registration = Registration.objects.get(
            student=self.waiting_student,
            event=self.event,
        )

        self.assertEqual(
            registration.status,
            Registration.Status.WAITLISTED,
        )

    def test_duplicate_active_registration_is_rejected(self):
        Registration.objects.create(
            student=self.student,
            event=self.event,
            status=Registration.Status.REGISTERED,
        )

        response = self.client.post(
            "/api/registrations/",
            {"event": self.event.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancelling_registration_promotes_waitlisted_student(self):
        first_registration = Registration.objects.create(
            student=self.student,
            event=self.event,
            status=Registration.Status.REGISTERED,
        )

        Registration.objects.create(
            student=self.waiting_student,
            event=self.event,
            status=Registration.Status.WAITLISTED,
        )

        response = self.client.post(
            f"/api/registrations/{first_registration.id}/cancel/",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_registration.refresh_from_db()

        promoted_registration = Registration.objects.get(
            student=self.waiting_student,
            event=self.event,
        )

        self.assertEqual(
            first_registration.status,
            Registration.Status.CANCELLED,
        )

        self.assertEqual(
            promoted_registration.status,
            Registration.Status.REGISTERED,
        )

        self.assertEqual(
            response.data["promoted_student"],
            self.waiting_student.username,
        )

    def test_user_can_only_see_own_registrations(self):
        own_registration = Registration.objects.create(
            student=self.student,
            event=self.event,
        )

        other_registration = Registration.objects.create(
            student=self.other_student,
            event=self.event,
        )

        response = self.client.get("/api/registrations/my/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]

        self.assertIn(own_registration.id, returned_ids)
        self.assertNotIn(other_registration.id, returned_ids)

    def test_club_representative_cannot_register(self):
        self.client.force_authenticate(user=self.representative)

        response = self.client.post(
            "/api/registrations/",
            {"event": self.event.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
