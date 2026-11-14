import { NextRequest, NextResponse } from "next/server";

import { withConsumerApiErrors } from "@/lib/api-route";
import { signup } from "@/lib/consumer-api";
import { setSessionCookie } from "@/lib/session";

export async function POST(request: NextRequest) {
  const { full_name, email, password } = await request.json();

  return withConsumerApiErrors(
    async () => {
      // Signup auto-logs the user in: consumer-api's POST /user mints and
      // returns an Access Token alongside the created user.
      const { access_token, user } = await signup({ full_name, email, password });
      const response = NextResponse.json({ user }, { status: 200 });
      setSessionCookie(response, access_token);
      return response;
    },
    (error) =>
      error.status === 409
        ? "That email is already registered. Try logging in instead."
        : "Could not create your account. Please try again.",
  );
}
