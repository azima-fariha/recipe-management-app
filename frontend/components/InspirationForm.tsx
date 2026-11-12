"use client";

import { useState, type FormEvent } from "react";

interface Recipe {
  id: string | null;
  name: string;
  ingredients: string[];
  instructions: string;
}

export function InspirationForm() {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [recipe, setRecipe] = useState<Recipe | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setRecipe(null);
    setLoading(true);

    const formData = new FormData(event.currentTarget);
    const query = String(formData.get("ingredients") ?? "");

    try {
      const response = await fetch("/api/inspiration", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      const body = await response.json().catch(() => null);
      if (!response.ok) {
        setError(body?.error ?? "Something went wrong. Please try again.");
        return;
      }
      setRecipe(body.recipe);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Find or invent a recipe</h1>
      <form onSubmit={handleSubmit}>
        <label>
          What ingredients do you have?
          <textarea
            name="ingredients"
            required
            disabled={loading}
            placeholder="e.g. eggs, flour, milk"
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Searching..." : "Find a recipe"}
        </button>
      </form>

      {loading && (
        <p role="status">Looking for a recipe... this can take a moment.</p>
      )}
      {error && <p role="alert">{error}</p>}

      {recipe && (
        <article>
          <h2>{recipe.name}</h2>
          <h3>Ingredients</h3>
          <ul>
            {recipe.ingredients.map((ingredient) => (
              <li key={ingredient}>{ingredient}</li>
            ))}
          </ul>
          <h3>Instructions</h3>
          <p>{recipe.instructions}</p>
        </article>
      )}
    </main>
  );
}
