import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""

    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        # Arrange: no setup needed beyond fixture

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_structure(self, client):
        """Test that activities have required fields"""
        # Arrange: no extra state changes

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_participants_list(self, client):
        """Test that participants are returned correctly"""
        # Arrange: no extra state modifications

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        chess_participants = data["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants