from beanie import Document

class Recipe(Document):
    name: str
    ingredients: list[str]
    instructions: str
    user_id: str

    class Settings:
        name = "recipes"
