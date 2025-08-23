import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestIssuePermissions:

    def setup_method(self):
        self.client = APIClient()

        self.author = User.objects.create_user(
            username="author", password="pass123"
        )
        self.other_user = User.objects.create_user(
            username="intruder", password="pass456"
        )

        # Authentification avec l’auteur
        self.client.force_authenticate(user=self.author)

        # Création du projet
        project_response = self.client.post("/api/projects/", {
            "title": "Projet permissions",
            "description": "Test des droits",
            "type": "AI"
        })
        assert project_response.status_code == 201
        project_id = project_response.data["id"]

        # Création de l’issue
        issue_response = self.client.post("/api/issues/", {
            "name": "Test autorisations",
            "description": "Doit être modifiable seulement par l’auteur",
            "tag": "TASK",
            "priority": "LOW",
            "status": "TODO",
            "project": project_id
        })
        assert issue_response.status_code == 201
        self.issue_id = issue_response.data["id"]

    def test_update_issue_by_author(self):
        response = self.client.patch(f"/api/issues/{self.issue_id}/", {
            "status": "DONE"
        })
        assert response.status_code == 200
        assert response.data["status"] == "DONE"

    def test_update_issue_by_other_user_should_fail(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(f"/api/issues/{self.issue_id}/", {
            "status": "IN_PROGRESS"
        })
        assert response.status_code == 403  # Forbidden
