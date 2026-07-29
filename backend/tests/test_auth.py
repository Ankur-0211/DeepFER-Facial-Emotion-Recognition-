from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login():
    email = "test@example.com"
    password = "StrongPass123!"

    register_response = client.post(
        "/api/v1/auth/register", json={"email": email, "password": password}
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    body = login_response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_duplicate_registration_rejected():
    email = "dup@example.com"
    client.post("/api/v1/auth/register", json={"email": email, "password": "abc12345"})
    response = client.post(
        "/api/v1/auth/register", json={"email": email, "password": "abc12345"}
    )
    assert response.status_code == 400