from types import SimpleNamespace
from unittest.mock import AsyncMock, patch


def _recipe(id: str, name: str, ingredients: list[str], instructions: str) -> SimpleNamespace:
    # A duck-typed stand-in for a Beanie `Recipe` document (mapper.to_dto only
    # reads these four attributes). Using the real `Recipe` class here would
    # require a live Mongo connection via `init_beanie`, which this seam
    # deliberately avoids — it mocks the repository (the DB I/O boundary) and
    # exercises the real service/route/mapper logic above it.
    return SimpleNamespace(id=id, name=name, ingredients=ingredients, instructions=instructions)


def test_list_recipes_returns_recipes_for_user(client):
    soup = _recipe("abc123", "Soup", ["water"], "Boil")
    salad = _recipe("def456", "Salad", ["lettuce"], "Toss")

    with patch("recipe_repository.get_recipes_by_user_id", new=AsyncMock(return_value=[soup, salad])):
        response = client.get("/user/1/recipe")

    assert response.status_code == 200
    body = response.json()
    assert [recipe["name"] for recipe in body] == ["Soup", "Salad"]
    assert body[0]["ingredients"] == ["water"]
    assert body[0]["instructions"] == "Boil"
    assert body[0]["id"] == soup.id


def test_list_recipes_returns_empty_list_when_user_has_no_recipes(client):
    with patch("recipe_repository.get_recipes_by_user_id", new=AsyncMock(return_value=[])):
        response = client.get("/user/1/recipe")

    assert response.status_code == 200
    assert response.json() == []
