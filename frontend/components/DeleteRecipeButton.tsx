"use client";

import { useRouter } from "next/navigation";

import { useApiAction } from "@/hooks/useApiAction";

export function DeleteRecipeButton({ recipeId }: { recipeId: string }) {
  const router = useRouter();
  const { pending, error, run } = useApiAction();

  async function handleDelete() {
    if (!window.confirm("Delete this recipe? This can't be undone.")) {
      return;
    }

    await run(() => fetch(`/api/recipes/${recipeId}`, { method: "DELETE" }), {
      onSuccess: () => {
        router.push("/recipes");
        router.refresh();
      },
      fallbackErrorMessage: "Could not delete the recipe. Please try again.",
    });
  }

  return (
    <div>
      {error && <p role="alert">{error}</p>}
      <button type="button" onClick={handleDelete} disabled={pending}>
        {pending ? "Deleting..." : "Delete recipe"}
      </button>
    </div>
  );
}
