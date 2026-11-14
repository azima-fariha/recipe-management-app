"use client";

import { useRouter } from "next/navigation";
import { type FormEvent } from "react";

import { useApiAction } from "@/hooks/useApiAction";
import type { ApiRecipe } from "@/lib/consumer-api";

interface RecipeFormProps {
  mode: "create" | "edit";
  /** Required (and used for initial values) when mode is "edit". */
  recipe?: ApiRecipe;
}

export function RecipeForm({ mode, recipe }: RecipeFormProps) {
  const router = useRouter();
  const { pending, error, run } = useApiAction();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const ingredients = String(formData.get("ingredients") ?? "")
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    const payload = {
      name: formData.get("name"),
      ingredients,
      instructions: formData.get("instructions"),
    };

    const url = mode === "create" ? "/api/recipes" : `/api/recipes/${recipe?.id}`;
    const method = mode === "create" ? "POST" : "PUT";

    await run<{ recipe: ApiRecipe }>(
      () =>
        fetch(url, {
          method,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }),
      {
        onSuccess: (body) => {
          router.push(`/recipes/${body.recipe.id}`);
          router.refresh();
        },
      },
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>{mode === "create" ? "New recipe" : "Edit recipe"}</h1>
      {error && <p role="alert">{error}</p>}
      <label>
        Name
        <input name="name" type="text" defaultValue={recipe?.name} required />
      </label>
      <label>
        Ingredients (one per line)
        <textarea name="ingredients" defaultValue={recipe?.ingredients.join("\n")} required />
      </label>
      <label>
        Instructions
        <textarea name="instructions" defaultValue={recipe?.instructions} required />
      </label>
      <button type="submit" disabled={pending}>
        {pending ? "Saving..." : "Save recipe"}
      </button>
    </form>
  );
}
