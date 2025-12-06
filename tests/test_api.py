from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity checks
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_duplicate_and_unregister_flow():
    activity = "Chess Club"
    email = "pytest-user@example.com"

    # Ensure a clean start: attempt to delete if present
    client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Sign up
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Verify participant present
    r2 = client.get("/activities")
    assert email in r2.json()[activity]["participants"]

    # Duplicate signup should be rejected
    r3 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r3.status_code == 400

    # Unregister the participant
    r4 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r4.status_code == 200
    assert "Unregistered" in r4.json().get("message", "")

    # Verify participant removed
    r5 = client.get("/activities")
    assert email not in r5.json()[activity]["participants"]

    # Deleting again should return 404
    r6 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r6.status_code == 404
