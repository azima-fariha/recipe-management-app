import { NextResponse } from "next/server";

import { clearSessionCookie } from "@/lib/session";

// No call to consumer-api: per the spec's no-revocation decision, logging
// out only means discarding the token wherever it's held — the frontend's
// concern, not the gateway's.
export async function POST() {
  const response = NextResponse.json({ ok: true }, { status: 200 });
  clearSessionCookie(response);
  return response;
}
