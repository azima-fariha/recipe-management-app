import { NextRequest, NextResponse } from "next/server";

import { ConsumerApiError, login } from "@/lib/consumer-api";
import { setSessionCookie } from "@/lib/session";

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();

  try {
    const { access_token, user } = await login(email, password);
    const response = NextResponse.json({ user }, { status: 200 });
    setSessionCookie(response, access_token);
    return response;
  } catch (error) {
    if (error instanceof ConsumerApiError) {
      return NextResponse.json(
        { error: "Invalid email or password" },
        { status: error.status },
      );
    }
    throw error;
  }
}
