import { NextRequest, NextResponse } from "next/server";

import { ConsumerApiError, createRecipe } from "@/lib/consumer-api";
import { decodeAccessToken, getSessionToken } from "@/lib/session";

// Creates a recipe owned by the session's own user. Forwards the Access
// Token from the cookie as `Authorization: Bearer <token>` — the same
// mechanism a non-browser API client would use directly against
// consumer-api (see GLOSSARY.md > Access Token).
export async function POST(request: NextRequest) {
  const token = getSessionToken(request);
  const payload = token ? decodeAccessToken(token) : null;
  if (!token || !payload) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  const { name, ingredients, instructions } = await request.json();

  try {
    const recipe = await createRecipe(payload.sub, token, { name, ingredients, instructions });
    return NextResponse.json({ recipe }, { status: 201 });
  } catch (error) {
    if (error instanceof ConsumerApiError) {
      return NextResponse.json(
        { error: "Could not create the recipe. Please try again." },
        { status: error.status },
      );
    }
    throw error;
  }
}
