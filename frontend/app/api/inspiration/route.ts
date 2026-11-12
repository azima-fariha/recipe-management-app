import { NextRequest, NextResponse } from "next/server";

import { unauthorizedResponse, withConsumerApiErrors } from "@/lib/api-route";
import { discoverRecipe } from "@/lib/consumer-api";
import { requireSession } from "@/lib/session";

export async function POST(request: NextRequest) {
  const session = requireSession(request);
  if (!session) {
    return unauthorizedResponse();
  }

  const { query } = await request.json();

  return withConsumerApiErrors(
    async () => {
      const recipe = await discoverRecipe(session.userId, session.token, query);
      return NextResponse.json({ recipe }, { status: 200 });
    },
    (error) =>
      error.status === 404
        ? "No recipe could be found or invented for those ingredients."
        : "Something went wrong finding a recipe. Please try again.",
  );
}
