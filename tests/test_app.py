from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_activities(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "lucas@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(signup_url, params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert new_email in participants


def test_signup_duplicate_participant_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(signup_url, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_deletes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"
    remove_url = f"/activities/{quote(activity_name)}/participants"

    # Act
    response = client.delete(remove_url, params={"email": email_to_remove})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email_to_remove not in participants


def test_remove_nonexistent_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "notfound@mergington.edu"
    remove_url = f"/activities/{quote(activity_name)}/participants"

    # Act
    response = client.delete(remove_url, params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_for_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"