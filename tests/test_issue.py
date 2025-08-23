import pytest
from rest_framework.test import APIClient
from authentication.models import User  # modèle custom

@pytest.mark.django_db
class TestIssueAPI:

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="issue_creator",
            password="pass1234",
            email="issue@example.com"
        )
        self.client.force_authenticate(user=self.user)

        project = self.client.post("/api/projects/", {
            "name": "Projet Test",
            "description": "Projet lié aux issues",
            "type": "back-end"
        })

        print(" Response projet:")
        print("Status:", project.status_code)
        print("Data:", project.data)

        self.project_id = project.data["id"]

        self.issue_data = {
            "name": "Problème critique",
            "description": "Détails du bug",
            "tag": "BUG",
            "priority": "HIGH",
            "status": "To Do",
            "project": self.project_id,
            "assignee": self.user.id  # Ajouté ici !
        }

        print("Données envoyées pour création d'issue :")
        print(self.issue_data)

    def test_create_issue(self):
        response = self.client.post("/api/issues/", self.issue_data)

        print(" Response issue (create):")
        print("Status:", response.status_code)
        print("Data:", response.data)

        assert response.status_code == 201
        assert response.data["name"] == self.issue_data["name"]

    def test_list_issues(self):
        self.client.post("/api/issues/", self.issue_data)
        response = self.client.get("/api/issues/")

        print(" Response issue (list):")
        print("Status:", response.status_code)
        print("Data:", response.data)

        assert response.status_code == 200
        assert len(response.data) >= 1
