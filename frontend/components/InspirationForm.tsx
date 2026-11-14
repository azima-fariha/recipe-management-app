"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";

import { useApiAction } from "@/hooks/useApiAction";

interface Recipe {
  id: string | null;
  name: string;
  ingredients: string[];
  instructions: string;
}

export function InspirationForm() {
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const { pending, error, run } = useApiAction();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setRecipe(null);

    const formData = new FormData(event.currentTarget);
    const query = String(formData.get("ingredients") ?? "");

    await run<{ recipe: Recipe }>(
      () =>
        fetch("/api/inspiration", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query }),
        }),
      { onSuccess: (body) => setRecipe(body.recipe) },
    );
  }

  return (
    <main>
      <p>
        <Link href="/">Back home</Link>
      </p>
      <h1>Find or invent a recipe</h1>
      <form onSubmit={handleSubmit}>
        <label>
          What ingredients do you have?
          <textarea
            name="ingredients"
            required
            disabled={pending}
            placeholder="e.g. eggs, flour, milk"
          />
        </label>
        <button type="submit" disabled={pending}>
          {pending ? "Searching..." : "Find a recipe"}
        </button>
      </form>

      {pending && (
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
