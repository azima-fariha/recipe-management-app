import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { ConsumerApiError, fetchRecipes } from "@/lib/consumer-api";
import { decodeAccessToken, SESSION_COOKIE_NAME } from "@/lib/session";

// Recipe list page. Route protection itself is enforced by middleware.ts;
// this component additionally redirects if the token turns out to be
// rejected by consumer-api (e.g. tampered, or valid-looking but revoked at
// the gateway), mirroring the pattern in app/page.tsx.
export default async function RecipesPage() {
  const token = cookies().get(SESSION_COOKIE_NAME)?.value;
  const payload = token ? decodeAccessToken(token) : null;

  if (!token || !payload) {
    redirect("/login");
  }

  let recipes;
  try {
    recipes = await fetchRecipes(payload.sub, token);
  } catch (error) {
    if (error instanceof ConsumerApiError && (error.status === 401 || error.status === 403)) {
      redirect("/login");
    }
    throw error;
  }

  return (
    <main>
      <p>
        <Link href="/">Back home</Link>
      </p>
      <h1>Your recipes</h1>
      <p>
        <Link href="/recipes/new">New recipe</Link>
      </p>
      {recipes.length === 0 ? (
        <p>You haven&apos;t saved any recipes yet.</p>
      ) : (
        <ul>
          {recipes.map((recipe) => (
            <li key={recipe.id}>
              <Link href={`/recipes/${recipe.id}`}>{recipe.name}</Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
