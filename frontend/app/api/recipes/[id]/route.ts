import { NextRequest, NextResponse } from "next/server";

import { ConsumerApiError, deleteRecipe, updateRecipe } from "@/lib/consumer-api";
import { decodeAccessToken, getSessionToken } from "@/lib/session";

interface RouteParams {
  params: { id: string };
}

function requireSession(request: NextRequest) {
  const token = getSessionToken(request);
  const payload = token ? decodeAccessToken(token) : null;
  if (!token || !payload) {
    return null;
  }
  return { token, userId: payload.sub };
}

// Updates a recipe owned by the session's own user. Forwards the Access
// Token from the cookie as `Authorization: Bearer <token>` (see
// GLOSSARY.md > Access Token) — consumer-api's own ownership check (see
// GLOSSARY.md > Ownership) rejects any id that isn't this user's.
export async function PUT(request: NextRequest, { params }: RouteParams) {
  const session = requireSession(request);
  if (!session) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  const { name, ingredients, instructions } = await request.json();

  try {
    const recipe = await updateRecipe(session.userId, params.id, session.token, {
      name,
      ingredients,
      instructions,
    });
    return NextResponse.json({ recipe }, { status: 200 });
  } catch (error) {
    if (error instanceof ConsumerApiError) {
      return NextResponse.json(
        { error: "Could not update the recipe. Please try again." },
        { status: error.status },
      );
    }
    throw error;
  }
}

export async function DELETE(request: NextRequest, { params }: RouteParams) {
  const session = requireSession(request);
  if (!session) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  try {
    await deleteRecipe(session.userId, params.id, session.token);
    return NextResponse.json({ ok: true }, { status: 200 });
  } catch (error) {
    if (error instanceof ConsumerApiError) {
      return NextResponse.json(
        { error: "Could not delete the recipe. Please try again." },
        { status: error.status },
      );
    }
    throw error;
  }
}
