import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { DeleteRecipeButton } from "@/components/DeleteRecipeButton";
import { ConsumerApiError, fetchRecipeById } from "@/lib/consumer-api";
import { decodeAccessToken, SESSION_COOKIE_NAME } from "@/lib/session";

interface RecipePageProps {
  params: { id: string };
}

// Single-recipe view page. Route protection itself is enforced by
// middleware.ts; this component additionally redirects on 401/403 from
// consumer-api, mirroring the pattern in app/page.tsx and app/recipes/page.tsx.
export default async function RecipePage({ params }: RecipePageProps) {
  const token = cookies().get(SESSION_COOKIE_NAME)?.value;
  const payload = token ? decodeAccessToken(token) : null;

  if (!token || !payload) {
    redirect("/login");
  }

  let recipe;
  try {
    recipe = await fetchRecipeById(payload.sub, params.id, token);
  } catch (error) {
    if (error instanceof ConsumerApiError && (error.status === 401 || error.status === 403)) {
      redirect("/login");
    }
    if (error instanceof ConsumerApiError && error.status === 404) {
      return (
        <main>
          <p>That recipe couldn&apos;t be found.</p>
          <Link href="/recipes">Back to your recipes</Link>
        </main>
      );
    }
    throw error;
  }

  return (
    <main>
      <p>
        <Link href="/recipes">Back to your recipes</Link>
      </p>
      <h1>{recipe.name}</h1>

      <h2>Ingredients</h2>
      <ul>
        {recipe.ingredients.map((ingredient, index) => (
          <li key={index}>{ingredient}</li>
        ))}
      </ul>

      <h2>Instructions</h2>
      <p>{recipe.instructions}</p>

      <p>
        <Link href={`/recipes/${recipe.id}/edit`}>Edit recipe</Link>
      </p>
      <DeleteRecipeButton recipeId={recipe.id} />
    </main>
  );
}
