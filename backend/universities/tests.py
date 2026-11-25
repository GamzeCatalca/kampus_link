
from rest_framework import status
from rest_framework.test import APITestCase

from .models import University


class UniversityAPITests(APITestCase):

    def setUp(self):
        self.active_university = University.objects.create(
            name="Active Test University",
            description="An active university.",
            website="https://active.example.com",
            is_active=True,
        )

        self.inactive_university = University.objects.create(
            name="Inactive Test University",
            is_active=False,
        )

    def test_list_returns_only_active_universities(self):
        response = self.client.get("/api/universities/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]

        self.assertIn(self.active_university.id, returned_ids)
        self.assertNotIn(self.inactive_university.id, returned_ids)

    def test_active_university_detail(self):
        response = self.client.get(
            f"/api/universities/{self.active_university.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["name"],
            "Active Test University",
        )

    def test_inactive_university_detail_returns_404(self):
        response = self.client.get(
            f"/api/universities/{self.inactive_university.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
