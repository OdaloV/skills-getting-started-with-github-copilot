import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    return TestClient(app)


class TestRemoveParticipant:
    """Test suite for DELETE /activities/{activity_name}/participants endpoint"""

    def test_successful_removal(self, client):
        """Test successful participant removal"""
        # Arrange
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert f"Unregistered {email}" in response.json()["message"]

    def test_removal_actually_removes(self, client):
        """Test that removal actually deletes participant"""
        # Arrange
        email = "emma@mergington.edu"

        # Act
        client.delete(
            "/activities/Programming Class/participants",
            params={"email": email}
        )

        # Assert
        response = client.get("/activities")
        participants = response.json()["Programming Class"]["participants"]
        assert email not in participants

    def test_remove_from_nonexistent_activity(self, client):
        """Test removal fails for non-existent activity"""
        # Arrange
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            "/activities/Fake Activity/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_nonexistent_participant(self, client):
        """Test removal fails for student not in activity"""
        # Arrange
        email = "notinactivity@mergington.edu"

        # Act
        response = client.delete(
            "/activities/Chess Club/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]

    def test_multiple_removals(self, client):
        """Test removing all participants from activity"""
        # Arrange
        activity_name = "Drama Club"

        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"].copy()

        # Act
        for email in initial_participants:
            response = client.delete(
                f"/activities/{activity_name}/participants",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert
        response = client.get("/activities")
        assert len(response.json()[activity_name]["participants"]) == 0