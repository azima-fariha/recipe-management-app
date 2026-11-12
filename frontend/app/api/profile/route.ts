import { NextRequest, NextResponse } from "next/server";

import { unauthorizedResponse, withConsumerApiErrors } from "@/lib/api-route";
import { deleteUser, updateUser } from "@/lib/consumer-api";
import { clearSessionCookie, requireSession } from "@/lib/session";

export async function PUT(request: NextRequest) {
  const session = requireSession(request);
  if (!session) {
    return unauthorizedResponse();
  }

  const updates = await request.json();

  return withConsumerApiErrors(
    async () => {
      const user = await updateUser(session.userId, session.token, updates);
      return NextResponse.json({ user }, { status: 200 });
    },
    () => "Could not update profile",
  );
}

export async function DELETE(request: NextRequest) {
  const session = requireSession(request);
  if (!session) {
    return unauthorizedResponse();
  }

  return withConsumerApiErrors(
    async () => {
      await deleteUser(session.userId, session.token);

      // Deleting the account ends the session: clear the cookie so the next
      // request (e.g. the redirect to /login) has nothing to pick up.
      const response = NextResponse.json({ ok: true }, { status: 200 });
      clearSessionCookie(response);
      return response;
    },
    () => "Could not delete account",
  );
}
