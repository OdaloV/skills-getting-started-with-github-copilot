import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    return TestClient(app)


class TestSignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup(self, client):
        """Test successful signup"""
        # Arrange
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert f"Signed up {email}" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to activity"""
        # Arrange
        email = "test@mergington.edu"

        # Act
        client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )

        # Assert
        response = client.get("/activities")
        participants = response.json()["Programming Class"]["participants"]
        assert email in participants

    def test_signup_nonexistent_activity(self, client):
        """Test signup fails for non-existent activity"""
        # Arrange
        email = "student@mergington.edu"

        # Act
        response = client.post(
            "/activities/Fake Activity/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_duplicate_signup(self, client):
        """Test that duplicate signup is rejected"""
        # Arrange
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_activities(self, client):
        """Test student can sign up for multiple activities"""
        # Arrange
        email = "multiactivity@mergington.edu"

        # Act
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200