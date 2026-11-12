"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function DeleteRecipeButton({ recipeId }: { recipeId: string }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  async function handleDelete() {
    if (!window.confirm("Delete this recipe? This can't be undone.")) {
      return;
    }

    setError(null);
    setDeleting(true);

    const response = await fetch(`/api/recipes/${recipeId}`, { method: "DELETE" });

    if (response.ok) {
      router.push("/recipes");
      router.refresh();
      return;
    }

    setDeleting(false);
    const body = await response.json().catch(() => null);
    setError(body?.error ?? "Could not delete the recipe. Please try again.");
  }

  return (
    <div>
      {error && <p role="alert">{error}</p>}
      <button type="button" onClick={handleDelete} disabled={deleting}>
        {deleting ? "Deleting..." : "Delete recipe"}
      </button>
    </div>
  );
}
