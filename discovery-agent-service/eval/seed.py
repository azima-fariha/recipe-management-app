import time
from dataclasses import dataclass

from checks import RecipeLike
from client import ConsumerApiClient


@dataclass
class EvalUser:
    user_id: str
    token: str
    dietary_restrictions: str
    preferences: str
    saved_recipe: RecipeLike


@dataclass
class SeededContext:
    user_a: EvalUser
    user_b: EvalUser


def seed_eval_users(client: ConsumerApiClient) -> SeededContext:
    """Creates two distinct eval users through the real signup flow, each with one saved
    recipe, so retrieval/groundedness/cross-user-isolation cases have real, known data to
    check results against."""
    run_id = str(int(time.time()))

    signup_a = client.signup(
        full_name="Eval User A",
        email=f"eval-a-{run_id}@example.com",
        password="eval-password-a",
        dietary_restrictions="vegetarian",
        preferences="loves spicy food",
    )
    recipe_a = RecipeLike(
        name="Spicy Chickpea Curry",
        ingredients=["chickpeas", "onion", "tomato", "chili", "garlic", "coconut milk"],
        instructions="Saute onion and garlic, add chili, tomato, chickpeas, and coconut milk, simmer 20 minutes.",
    )
    client.create_recipe(
        signup_a["user"]["id"], signup_a["access_token"], recipe_a.name, recipe_a.ingredients, recipe_a.instructions
    )

    signup_b = client.signup(
        full_name="Eval User B",
        email=f"eval-b-{run_id}@example.com",
        password="eval-password-b",
        dietary_restrictions="vegan",
        preferences="prefers quick meals",
    )
    recipe_b = RecipeLike(
        name="Vegan Peanut Noodles",
        ingredients=["noodles", "peanut butter", "soy sauce", "lime", "garlic"],
        instructions="Cook noodles, whisk peanut butter with soy sauce and lime, toss together with garlic.",
    )
    client.create_recipe(
        signup_b["user"]["id"], signup_b["access_token"], recipe_b.name, recipe_b.ingredients, recipe_b.instructions
    )

    return SeededContext(
        user_a=EvalUser(
            user_id=str(signup_a["user"]["id"]),
            token=signup_a["access_token"],
            dietary_restrictions="vegetarian",
            preferences="loves spicy food",
            saved_recipe=recipe_a,
        ),
        user_b=EvalUser(
            user_id=str(signup_b["user"]["id"]),
            token=signup_b["access_token"],
            dietary_restrictions="vegan",
            preferences="prefers quick meals",
            saved_recipe=recipe_b,
        ),
    )
