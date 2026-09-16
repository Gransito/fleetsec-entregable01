from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200


def test_login_and_protected_endpoint():
    with TestClient(app) as client:
        response = client.post(
            "/login",
            json={"username": "demo", "password": "DemoPass123!"},
        )

        assert response.status_code == 200

        token = response.json()["access_token"]

        protected = client.get(
            "/vehicles",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert protected.status_code == 200
        assert len(protected.json()) >= 1


def test_protected_endpoint_requires_token():
    with TestClient(app) as client:
        assert client.get("/vehicles").status_code in (401, 403)

