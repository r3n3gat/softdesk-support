import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestAuthentication:

    def setup_method(self):
        self.client = APIClient()
        self.user_data = {
            "username": "testuser",
            "password": "testpass123",
            "email": "testuser@example.com"
        }

    def test_signup(self):
        response = self.client.post("/api/signup/", self.user_data)
        assert response.status_code == 201
        assert "id" in response.data

    def test_login(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post("/api/login/", {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })
        assert response.status_code == 200
        assert "access" in response.data or "token" in response.data  # selon ton implémentation JWT

    def test_get_profile(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/me/")
        assert response.status_code == 200
        assert response.data["username"] == self.user_data["username"]
