import { NextRequest, NextResponse } from "next/server";

import { ConsumerApiError, discoverRecipe } from "@/lib/consumer-api";
import { decodeAccessToken, getSessionToken } from "@/lib/session";

export async function POST(request: NextRequest) {
  const token = getSessionToken(request);
  const payload = token ? decodeAccessToken(token) : null;

  if (!token || !payload) {
    return NextResponse.json({ error: "Not logged in" }, { status: 401 });
  }

  const { query } = await request.json();

  try {
    const recipe = await discoverRecipe(payload.sub, token, query);
    return NextResponse.json({ recipe }, { status: 200 });
  } catch (error) {
    if (error instanceof ConsumerApiError) {
      const message =
        error.status === 404
          ? "No recipe could be found or invented for those ingredients."
          : "Something went wrong finding a recipe. Please try again.";
      return NextResponse.json({ error: message }, { status: error.status });
    }
    throw error;
  }
}
