import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Keep a shallow copy of initial participants to restore after each test
    original = {
        name: data["participants"].copy() for name, data in activities.items()
    }
    yield
    # restore
    for name, parts in original.items():
        activities[name]["participants"] = parts


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_student@mergington.edu"

    # Ensure not already present
    assert email not in activities[activity]["participants"]

    # Sign up
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    json = res.json()
    assert "Signed up" in json["message"]
    assert email in activities[activity]["participants"]

    # Signing up again should fail
    res2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert res2.status_code == 400

    # Unregister
    res3 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert res3.status_code == 200
    json3 = res3.json()
    assert "Unregistered" in json3["message"]
    assert email not in activities[activity]["participants"]

    # Unregistering again should fail
    res4 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert res4.status_code == 400
