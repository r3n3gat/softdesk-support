# tests/test_projects.py (version alignée specs)

import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestProjectAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="devuser",
            password="strongpass",
            email="dev@example.com"
        )
        self.client.force_authenticate(user=self.user)
        self.project_data = {
            "name": "Plateforme Tickets",
            "description": "Outil de suivi",
            "type": "BACKEND"  # <- valeur valide
        }

    def test_create_project(self):
        response = self.client.post("/api/projects/", self.project_data, format='json')
        assert response.status_code == 201
        assert response.data["name"] == self.project_data["name"]

    def test_list_projects(self):
        create_response = self.client.post("/api/projects/", self.project_data, format='json')
        assert create_response.status_code == 201
        list_response = self.client.get("/api/projects/")
        assert list_response.status_code == 200
        assert any(p["name"] == self.project_data["name"] for p in list_response.data)
