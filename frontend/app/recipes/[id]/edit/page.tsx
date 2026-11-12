import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { RecipeForm } from "@/components/RecipeForm";
import { ConsumerApiError, fetchRecipeById } from "@/lib/consumer-api";
import { decodeAccessToken, SESSION_COOKIE_NAME } from "@/lib/session";

interface EditRecipePageProps {
  params: { id: string };
}

// Edit-recipe page. Route protection itself is enforced by middleware.ts;
// this component additionally redirects on 401/403 from consumer-api,
// mirroring the pattern in app/page.tsx and app/recipes/page.tsx.
export default async function EditRecipePage({ params }: EditRecipePageProps) {
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
    throw error;
  }

  return <RecipeForm mode="edit" recipe={recipe} />;
}
