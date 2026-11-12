import { NextRequest, NextResponse } from "next/server";

import { unauthorizedResponse, withConsumerApiErrors } from "@/lib/api-route";
import { createRecipe } from "@/lib/consumer-api";
import { requireSession } from "@/lib/session";

// Creates a recipe owned by the session's own user. Forwards the Access
// Token from the cookie as `Authorization: Bearer <token>` — the same
// mechanism a non-browser API client would use directly against
// consumer-api (see GLOSSARY.md > Access Token).
export async function POST(request: NextRequest) {
  const session = requireSession(request);
  if (!session) {
    return unauthorizedResponse();
  }

  const { name, ingredients, instructions } = await request.json();

  return withConsumerApiErrors(
    async () => {
      const recipe = await createRecipe(session.userId, session.token, {
        name,
        ingredients,
        instructions,
      });
      return NextResponse.json({ recipe }, { status: 201 });
    },
    () => "Could not create the recipe. Please try again.",
  );
}
