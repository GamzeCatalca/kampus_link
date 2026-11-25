
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from universities.models import University
from .models import Club

User = get_user_model()


class ClubAPITests(APITestCase):

    def setUp(self):
        self.university = University.objects.create(
            name="Club Test University",
        )

        self.student = User.objects.create_user(
            username="club_test_student",
            password="StrongPass123!",
        )

        self.other_student = User.objects.create_user(
            username="other_club_student",
            password="StrongPass123!",
        )

        self.client.force_authenticate(user=self.student)

    def test_student_can_apply_for_club(self):
        response = self.client.post(
            "/api/clubs/create/",
            {
                "university": self.university.id,
                "name": "Test Software Club",
                "description": "A test club.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        club = Club.objects.get(name="Test Software Club")

        self.assertEqual(club.status, Club.Status.PENDING)
        self.assertEqual(club.representative, self.student)

    def test_pending_club_is_not_publicly_listed(self):
        pending_club = Club.objects.create(
            university=self.university,
            name="Pending Test Club",
            representative=self.student,
            status=Club.Status.PENDING,
        )

        response = self.client.get("/api/clubs/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]

        self.assertNotIn(pending_club.id, returned_ids)

    def test_user_sees_only_own_club_applications(self):
        own_club = Club.objects.create(
            university=self.university,
            name="Own Test Club",
            representative=self.student,
        )

        other_club = Club.objects.create(
            university=self.university,
            name="Other Test Club",
            representative=self.other_student,
        )

        response = self.client.get("/api/clubs/my/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]

        self.assertIn(own_club.id, returned_ids)
        self.assertNotIn(other_club.id, returned_ids)
