
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from universities.models import University
from clubs.models import Club
from .models import Event

User = get_user_model()


class EventAPITests(APITestCase):

    def setUp(self):
        self.university = University.objects.create(
            name="Event Test University",
        )

        self.student = User.objects.create_user(
            username="event_test_student",
            password="StrongPass123!",
            role="STUDENT",
        )

        self.representative = User.objects.create_user(
            username="event_test_rep",
            password="StrongPass123!",
            role="CLUB_REP",
        )

        self.other_representative = User.objects.create_user(
            username="other_event_rep",
            password="StrongPass123!",
            role="CLUB_REP",
        )

        self.club = Club.objects.create(
            university=self.university,
            name="Event Test Club",
            representative=self.representative,
            status=Club.Status.APPROVED,
        )

        self.other_club = Club.objects.create(
            university=self.university,
            name="Other Event Test Club",
            representative=self.other_representative,
            status=Club.Status.APPROVED,
        )

        self.start = timezone.now() + timedelta(days=5)
        self.end = self.start + timedelta(hours=2)

        self.published_event = Event.objects.create(
            club=self.club,
            title="Published Test Event",
            description="A published test event.",
            location="Istanbul",
            start_datetime=self.start,
            end_datetime=self.end,
            status=Event.Status.PUBLISHED,
            created_by=self.representative,
        )

        self.draft_event = Event.objects.create(
            club=self.club,
            title="Draft Test Event",
            description="A draft test event.",
            location="Istanbul",
            start_datetime=self.start,
            end_datetime=self.end,
            status=Event.Status.DRAFT,
            created_by=self.representative,
        )

    def event_payload(self, club_id):
        return {
            "club": club_id,
            "title": "New Test Event",
            "description": "An event created during testing.",
            "location": "Istanbul",
            "start_datetime": self.start.isoformat(),
            "end_datetime": self.end.isoformat(),
        }

    def test_public_list_shows_only_published_events(self):
        response = self.client.get("/api/events/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [
            item["id"] for item in response.data["results"]
        ]

        self.assertIn(self.published_event.id, returned_ids)
        self.assertNotIn(self.draft_event.id, returned_ids)

    def test_student_cannot_create_event(self):
        self.client.force_authenticate(user=self.student)

        response = self.client.post(
            "/api/events/create/",
            self.event_payload(self.club.id),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_representative_can_create_event_for_own_club(self):
        self.client.force_authenticate(user=self.representative)

        response = self.client.post(
            "/api/events/create/",
            self.event_payload(self.club.id),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        event = Event.objects.get(title="New Test Event")

        self.assertEqual(event.club, self.club)
        self.assertEqual(event.created_by, self.representative)
        self.assertEqual(event.status, Event.Status.DRAFT)

    def test_representative_cannot_create_event_for_another_club(self):
        self.client.force_authenticate(user=self.representative)

        response = self.client.post(
            "/api/events/create/",
            self.event_payload(self.other_club.id),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_representative_cannot_update_another_clubs_event(self):
        self.client.force_authenticate(user=self.other_representative)

        response = self.client.patch(
            f"/api/events/{self.published_event.id}/update/",
            {"title": "Unauthorized Update"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_draft_event_is_not_publicly_accessible(self):
        response = self.client.get(
            f"/api/events/{self.draft_event.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
