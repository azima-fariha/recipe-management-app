import httpx

DEFAULT_CONSUMER_API_URL = "http://localhost:8088"


class ConsumerApiClient:
    """Thin wrapper over consumer-api's real HTTP endpoints, used to seed eval fixtures and
    exercise the inspiration flow exactly as a real client would — through real auth, not a
    mocked shortcut."""

    def __init__(self, base_url: str = DEFAULT_CONSUMER_API_URL, timeout: float = 60.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def signup(
        self,
        full_name: str,
        email: str,
        password: str,
        dietary_restrictions: str | None = None,
        preferences: str | None = None,
    ) -> dict:
        response = self._client.post(
            "/user",
            json={
                "full_name": full_name,
                "email": email,
                "password": password,
                "dietary_restrictions": dietary_restrictions,
                "preferences": preferences,
            },
        )
        response.raise_for_status()
        return response.json()

    def create_recipe(self, user_id: str, token: str, name: str, ingredients: list[str], instructions: str) -> dict:
        response = self._client.post(
            f"/user/{user_id}/recipe",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": name, "ingredients": ingredients, "instructions": instructions},
        )
        response.raise_for_status()
        return response.json()

    def discover(self, user_id: str, token: str, query: str) -> tuple[int, dict]:
        """Returns (status_code, body) — a 404 ("nothing found") is a valid outcome, not an error."""
        response = self._client.post(
            f"/user/{user_id}/inspiration",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": query},
        )
        if response.status_code == 404:
            return response.status_code, {}
        response.raise_for_status()
        return response.status_code, response.json()

    def close(self) -> None:
        self._client.close()
