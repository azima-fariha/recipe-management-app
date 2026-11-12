import datetime

import httpx
import jwt
import pytest
import respx

import auth

PROTECTED_ROUTES = [
    ("get", "/user/1"),
    ("put", "/user/1"),
    ("delete", "/user/1"),
    ("get", "/user/1/recipe"),
    ("get", "/user/1/recipe/abc"),
    ("post", "/user/1/recipe"),
    ("put", "/user/1/recipe/abc"),
    ("delete", "/user/1/recipe/abc"),
    ("post", "/user/1/inspiration"),
]


def _mock_user_service_fetch(user_id: int = 1):
    respx.get(f"http://localhost:8081/user/{user_id}").mock(
        return_value=httpx.Response(
            200,
            json={"id": user_id, "full_name": "Ada Lovelace", "email": "ada@example.com"},
        )
    )


def test_get_user_rejects_missing_token(client):
    response = client.get("/user/1")

    assert response.status_code == 401


def test_get_user_rejects_malformed_token(client):
    response = client.get("/user/1", headers={"Authorization": "Bearer not-a-real-jwt"})

    assert response.status_code == 401


def test_get_user_rejects_expired_token(client):
    now = datetime.datetime.now(datetime.timezone.utc)
    expired_token = jwt.encode(
        {"sub": "1", "iat": now - datetime.timedelta(days=8), "exp": now - datetime.timedelta(days=1)},
        auth.JWT_SECRET_KEY,
        algorithm=auth.JWT_ALGORITHM,
    )

    response = client.get("/user/1", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401


def test_get_user_rejects_mismatched_token_subject(client):
    token = auth.create_access_token(subject="2")

    response = client.get("/user/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403


def test_get_user_succeeds_with_matching_token(client):
    token = auth.create_access_token(subject="1")

    with respx.mock:
        _mock_user_service_fetch(user_id=1)
        response = client.get("/user/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "ada@example.com"


@pytest.mark.parametrize("method,path", PROTECTED_ROUTES)
def test_every_user_id_route_rejects_missing_token(client, method, path):
    response = client.request(method.upper(), path, json={})

    assert response.status_code == 401


@pytest.mark.parametrize("method,path", PROTECTED_ROUTES)
def test_every_user_id_route_rejects_mismatched_token_subject(client, method, path):
    token = auth.create_access_token(subject="2")

    response = client.request(
        method.upper(), path, json={}, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_delete_user_rejects_missing_token(client):
    response = client.delete("/user/1")

    assert response.status_code == 401


def test_delete_user_rejects_mismatched_token_subject(client):
    token = auth.create_access_token(subject="2")

    response = client.delete("/user/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403


def test_delete_user_succeeds_with_matching_token(client):
    token = auth.create_access_token(subject="1")

    with respx.mock:
        respx.delete("http://localhost:8081/user/1").mock(return_value=httpx.Response(200))
        response = client.delete("/user/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 204


def test_update_user_succeeds_with_matching_token(client):
    token = auth.create_access_token(subject="1")

    with respx.mock:
        respx.put("http://localhost:8081/user/1").mock(
            return_value=httpx.Response(200, json={"full_name": "Ada L."})
        )
        response = client.put(
            "/user/1",
            json={"full_name": "Ada L."},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Ada L."


def test_fetch_recipe_succeeds_with_matching_token(client):
    token = auth.create_access_token(subject="1")

    with respx.mock:
        respx.get("http://localhost:8082/user/1/recipe/abc").mock(
            return_value=httpx.Response(
                200,
                json={"id": "abc", "name": "Soup", "ingredients": ["water"], "instructions": "Boil"},
            )
        )
        response = client.get(
            "/user/1/recipe/abc", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Soup"


def test_create_recipe_succeeds_with_matching_token(client):
    token = auth.create_access_token(subject="1")

    with respx.mock:
        respx.post("http://localhost:8082/user/1/recipe").mock(
            return_value=httpx.Response(
                200,
                json={"id": "abc", "name": "Soup", "ingredients": ["water"], "instructions": "Boil"},
            )
        )
        response = client.post(
            "/user/1/recipe",
            json={"name": "Soup", "ingredients": ["water"], "instructions": "Boil"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Soup"


def test_update_recipe_succeeds_with_matching_token(client):
    token = auth.create_access_token(subject="1")

    with respx.mock:
        respx.put("http://localhost:8082/user/1/recipe/abc").mock(
            return_value=httpx.Response(
                200,
                json={"id": "abc", "name": "Soup v2", "ingredients": ["water"], "instructions": "Boil"},
            )
        )
        response = client.put(
            "/user/1/recipe/abc",
            json={"name": "Soup v2"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Soup v2"


def test_delete_recipe_succeeds_with_matching_token(client):
    token = auth.create_access_token(subject="1")

    with respx.mock:
        respx.delete("http://localhost:8082/user/1/recipe/abc").mock(
            return_value=httpx.Response(204)
        )
        response = client.delete(
            "/user/1/recipe/abc", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 204


def test_list_recipes_succeeds_with_matching_token(client):
    token = auth.create_access_token(subject="1")

    with respx.mock:
        respx.get("http://localhost:8082/user/1/recipe").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {"id": "abc", "name": "Soup", "ingredients": ["water"], "instructions": "Boil"},
                    {"id": "def", "name": "Salad", "ingredients": ["lettuce"], "instructions": "Toss"},
                ],
            )
        )
        response = client.get("/user/1/recipe", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert [recipe["name"] for recipe in body] == ["Soup", "Salad"]


def test_discover_recipe_succeeds_with_matching_token(client):
    token = auth.create_access_token(subject="1")

    with respx.mock:
        respx.post("http://localhost:8084/user/1/discover-recipes").mock(
            return_value=httpx.Response(
                200,
                json={"id": "abc", "name": "Soup", "ingredients": ["water"], "instructions": "Boil"},
            )
        )
        response = client.post(
            "/user/1/inspiration",
            json={"query": "water"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Soup"
