
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AccountAPITests(APITestCase):

    def test_user_can_register(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "test_student",
                "email": "student@example.com",
                "first_name": "Test",
                "last_name": "Student",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="test_student")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertEqual(user.role, User.Role.STUDENT)

    def test_profile_requires_authentication(self):
        response = self.client.get("/api/auth/profile/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_view_profile(self):
        user = User.objects.create_user(
            username="profile_student",
            email="profile@example.com",
            password="StrongPass123!",
        )

        self.client.force_authenticate(user=user)

        response = self.client.get("/api/auth/profile/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "profile_student")
        self.assertEqual(response.data["email"], "profile@example.com")
        self.assertEqual(response.data["role"], User.Role.STUDENT)
