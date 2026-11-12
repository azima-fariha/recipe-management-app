import { NextRequest, NextResponse } from "next/server";

import { unauthorizedResponse, withConsumerApiErrors } from "@/lib/api-route";
import { deleteRecipe, updateRecipe } from "@/lib/consumer-api";
import { requireSession } from "@/lib/session";

interface RouteParams {
  params: { id: string };
}

// Updates a recipe owned by the session's own user. Forwards the Access
// Token from the cookie as `Authorization: Bearer <token>` (see
// GLOSSARY.md > Access Token) — consumer-api's own ownership check (see
// GLOSSARY.md > Ownership) rejects any id that isn't this user's.
export async function PUT(request: NextRequest, { params }: RouteParams) {
  const session = requireSession(request);
  if (!session) {
    return unauthorizedResponse();
  }

  const { name, ingredients, instructions } = await request.json();

  return withConsumerApiErrors(
    async () => {
      const recipe = await updateRecipe(session.userId, params.id, session.token, {
        name,
        ingredients,
        instructions,
      });
      return NextResponse.json({ recipe }, { status: 200 });
    },
    () => "Could not update the recipe. Please try again.",
  );
}

export async function DELETE(request: NextRequest, { params }: RouteParams) {
  const session = requireSession(request);
  if (!session) {
    return unauthorizedResponse();
  }

  return withConsumerApiErrors(
    async () => {
      await deleteRecipe(session.userId, params.id, session.token);
      return NextResponse.json({ ok: true }, { status: 200 });
    },
    () => "Could not delete the recipe. Please try again.",
  );
}
