import { NextRequest, NextResponse } from "next/server";

import { ConsumerApiError, deleteUser, updateUser } from "@/lib/consumer-api";
import { clearSessionCookie, decodeAccessToken, SESSION_COOKIE_NAME } from "@/lib/session";

/**
 * Reads the Access Token out of this request's own session cookie (never a
 * browser-visible value) and the user id it belongs to. Returns null when
 * there's no usable session — middleware.ts already redirects page
 * navigations without one, but this route can also be reached directly, so
 * it checks again rather than trusting the caller.
 */
function getSession(request: NextRequest): { token: string; userId: string } | null {
  const token = request.cookies.get(SESSION_COOKIE_NAME)?.value;
  const payload = token ? decodeAccessToken(token) : null;
  if (!token || !payload) {
    return null;
  }
  return { token, userId: payload.sub };
}

export async function PUT(request: NextRequest) {
  const session = getSession(request);
  if (!session) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  const updates = await request.json();

  try {
    const user = await updateUser(session.userId, session.token, updates);
    return NextResponse.json({ user }, { status: 200 });
  } catch (error) {
    if (error instanceof ConsumerApiError) {
      return NextResponse.json(
        { error: "Could not update profile" },
        { status: error.status },
      );
    }
    throw error;
  }
}

export async function DELETE(request: NextRequest) {
  const session = getSession(request);
  if (!session) {
    return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
  }

  try {
    await deleteUser(session.userId, session.token);
  } catch (error) {
    if (error instanceof ConsumerApiError) {
      return NextResponse.json(
        { error: "Could not delete account" },
        { status: error.status },
      );
    }
    throw error;
  }

  // Deleting the account ends the session: clear the cookie so the next
  // request (e.g. the redirect to /login) has nothing to pick up.
  const response = NextResponse.json({ ok: true }, { status: 200 });
  clearSessionCookie(response);
  return response;
}
