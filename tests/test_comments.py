import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestCommentAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="commenter",
            password="mypassword",
            email="commenter@example.com"
        )
        self.client.force_authenticate(user=self.user)

        # Création d’un projet
        project_response = self.client.post("/api/projects/", {
            "title": "Projet avec commentaires",
            "description": "On teste les commentaires",
            "type": "Infrastructure"
        })
        assert project_response.status_code == 201
        project_id = project_response.data["id"]

        # Création d’une issue
        issue_response = self.client.post("/api/issues/", {
            "name": "Serveur en panne",
            "description": "Le serveur ne démarre plus",
            "tag": "BUG",
            "priority": "HIGH",
            "status": "TODO",
            "project": project_id
        })
        assert issue_response.status_code == 201
        self.issue_id = issue_response.data["id"]

        self.comment_data = {
            "description": "Je prends en charge cette issue",
            "issue": self.issue_id
        }

    def test_create_comment(self):
        response = self.client.post("/api/comments/", self.comment_data)
        assert response.status_code == 201
        assert response.data["description"] == self.comment_data["description"]

    def test_list_comments(self):
        self.client.post("/api/comments/", self.comment_data)
        response = self.client.get("/api/comments/")
        assert response.status_code == 200
        assert any(c["description"] == self.comment_data["description"] for c in response.data)
