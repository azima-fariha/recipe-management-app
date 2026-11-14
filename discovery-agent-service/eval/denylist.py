INEDIBLE_DENYLIST = [
    "bleach",
    "antifreeze",
    "rat poison",
    "detergent",
    "motor oil",
    "drain cleaner",
    "pesticide",
    "gasoline",
    "battery acid",
    "asbestos",
]


def denylisted_ingredients(ingredients: list[str]) -> list[str]:
    """Deterministic backstop: flag any ingredient that's an outright inedible/toxic item.

    This is intentionally a blunt, literal check — it exists to catch the clearest cases with
    zero ambiguity, as a second line of defense alongside the Hallucination judge, not to
    replace it.
    """
    hits = []
    for ingredient in ingredients:
        lowered = ingredient.lower()
        if any(banned in lowered for banned in INEDIBLE_DENYLIST):
            hits.append(ingredient)
    return hits
