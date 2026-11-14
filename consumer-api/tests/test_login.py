import httpx
import respx


def test_login_succeeds_with_valid_credentials(client):
    with respx.mock:
        respx.post("http://localhost:8081/internal/users/verify-credentials").mock(
            return_value=httpx.Response(
                200,
                json={"id": 1, "full_name": "Ada Lovelace", "email": "ada@example.com"},
            )
        )

        response = client.post(
            "/auth/login", json={"email": "ada@example.com", "password": "s3cr3t-pass"}
        )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["user"]["email"] == "ada@example.com"


def test_login_fails_with_wrong_password(client):
    with respx.mock:
        respx.post("http://localhost:8081/internal/users/verify-credentials").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid email or password"})
        )

        response = client.post(
            "/auth/login", json={"email": "ada@example.com", "password": "wrong-password"}
        )

    assert response.status_code == 401
