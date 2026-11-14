from denylist import denylisted_ingredients


def test_flags_an_outright_toxic_ingredient():
    assert denylisted_ingredients(["flour", "bleach", "sugar"]) == ["bleach"]


def test_is_case_insensitive():
    assert denylisted_ingredients(["Bleach"]) == ["Bleach"]


def test_returns_empty_list_when_nothing_flagged():
    assert denylisted_ingredients(["flour", "sugar", "eggs"]) == []


def test_flags_multiple_hits():
    assert denylisted_ingredients(["bleach", "flour", "antifreeze"]) == ["bleach", "antifreeze"]
