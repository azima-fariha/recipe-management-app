import { NextRequest, NextResponse } from "next/server";

import { getSessionToken, isSessionValid } from "@/lib/session";

// Pages reachable without a session: visitors land here to sign up or log in.
const PUBLIC_PATHS = new Set(["/login", "/signup"]);

/**
 * Enforces the "no page but /login and /signup is reachable without a
 * session" rule (see spec.md, Implementation Decisions > Frontend). Runs
 * before every page request except the auth API routes and Next internals
 * (see `config.matcher`).
 */
export function middleware(request: NextRequest) {
  if (PUBLIC_PATHS.has(request.nextUrl.pathname)) {
    return NextResponse.next();
  }

  const token = getSessionToken(request);
  if (!isSessionValid(token)) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api/auth|_next/static|_next/image|favicon.ico).*)"],
};
