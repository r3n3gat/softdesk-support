import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        return User.objects.create_user(
            username=kwargs.get("username", "testuser"),
            email=kwargs.get("email", "test@example.com"),
            password=kwargs.get("password", "pass1234")
        )
    return _create_user

@pytest.fixture
def authenticated_client(create_user):
    user = create_user()
    client = APIClient()
    response = client.post("/api/auth/login/", {
        "username": user.username,
        "password": "pass1234"
    })
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client
