def test_signup_requires_a_password(client):
    response = client.post(
        "/user",
        json={"full_name": "Ada Lovelace", "email": "ada@example.com"},
    )

    assert response.status_code == 422


def test_signup_never_returns_the_password(client):
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
    assert "password" not in body
    assert "password_hash" not in body


def test_signup_rejects_a_duplicate_email(client):
    client.post(
        "/user",
        json={
            "full_name": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "s3cr3t-pass",
        },
    )

    response = client.post(
        "/user",
        json={
            "full_name": "Ada Lovelace Jr.",
            "email": "ada@example.com",
            "password": "another-pass",
        },
    )

    assert response.status_code == 409
