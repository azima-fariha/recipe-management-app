from checks import RecipeLike
from golden_set import ADVERSARIAL, CROSS_USER_ISOLATION, RETRIEVAL, build_cases
from seed import EvalUser, SeededContext


def _fixture_context() -> SeededContext:
    recipe_a = RecipeLike(name="A's Dish", ingredients=["x"], instructions="x")
    recipe_b = RecipeLike(name="B's Dish", ingredients=["y"], instructions="y")
    return SeededContext(
        user_a=EvalUser("1", "token-a", "vegetarian", "spicy", recipe_a),
        user_b=EvalUser("2", "token-b", "vegan", "quick", recipe_b),
    )


def test_builds_fifteen_cases_with_unique_ids():
    cases = build_cases(_fixture_context())
    assert len(cases) == 15
    assert len({case.id for case in cases}) == 15


def test_every_category_from_the_grilling_session_is_represented():
    cases = build_cases(_fixture_context())
    categories = {case.category for case in cases}
    assert RETRIEVAL in categories
    assert CROSS_USER_ISOLATION in categories
    assert ADVERSARIAL in categories


def test_user_id_smuggling_case_references_the_other_users_real_id():
    cases = build_cases(_fixture_context())
    case = next(c for c in cases if c.id == "adversarial-user-id-smuggling")
    assert case.other_user is not None
    assert case.other_user.user_id == "2"
