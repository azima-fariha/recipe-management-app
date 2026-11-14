import httpx
import respx


def test_signup_logs_the_user_in_immediately(client):
    with respx.mock:
        respx.post("http://localhost:8081/user").mock(
            return_value=httpx.Response(
                200,
                json={"id": 1, "full_name": "Ada Lovelace", "email": "ada@example.com"},
            )
        )

        response = client.post(
            "/user",
            json={
                "full_name": "Ada Lovelace",
                "email": "ada@example.com",
                "password": "s3cr3t-pass",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["user"]["email"] == "ada@example.com"


def test_signup_rejects_a_duplicate_email(client):
    with respx.mock:
        respx.post("http://localhost:8081/user").mock(
            return_value=httpx.Response(409, json={"detail": "Email is already registered"})
        )

        response = client.post(
            "/user",
            json={
                "full_name": "Ada Lovelace",
                "email": "ada@example.com",
                "password": "s3cr3t-pass",
            },
        )

    assert response.status_code == 409
