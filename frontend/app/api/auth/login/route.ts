import { NextRequest, NextResponse } from "next/server";

import { withConsumerApiErrors } from "@/lib/api-route";
import { login } from "@/lib/consumer-api";
import { setSessionCookie } from "@/lib/session";

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();

  return withConsumerApiErrors(
    async () => {
      const { access_token, user } = await login(email, password);
      const response = NextResponse.json({ user }, { status: 200 });
      setSessionCookie(response, access_token);
      return response;
    },
    () => "Invalid email or password",
  );
}
