def test_verify_credentials_succeeds_with_correct_password(client):
    client.post(
        "/user",
        json={
            "full_name": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "s3cr3t-pass",
        },
    )

    response = client.post(
        "/internal/users/verify-credentials",
        json={"email": "ada@example.com", "password": "s3cr3t-pass"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "ada@example.com"
    assert "password" not in body
    assert "password_hash" not in body


def test_verify_credentials_fails_with_wrong_password(client):
    client.post(
        "/user",
        json={
            "full_name": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "s3cr3t-pass",
        },
    )

    response = client.post(
        "/internal/users/verify-credentials",
        json={"email": "ada@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_verify_credentials_fails_identically_for_unknown_email(client):
    client.post(
        "/user",
        json={
            "full_name": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "s3cr3t-pass",
        },
    )

    wrong_password_response = client.post(
        "/internal/users/verify-credentials",
        json={"email": "ada@example.com", "password": "wrong-password"},
    )
    unknown_email_response = client.post(
        "/internal/users/verify-credentials",
        json={"email": "unknown@example.com", "password": "whatever"},
    )

    assert unknown_email_response.status_code == 401
    assert unknown_email_response.status_code == wrong_password_response.status_code
    assert unknown_email_response.json() == wrong_password_response.json()
