import type { NextRequest, NextResponse } from "next/server";

/**
 * The Access Token (see GLOSSARY.md) lives only in this cookie, and only
 * between the browser and the Next.js server — consumer-api never sees a
 * cookie, only the `Authorization: Bearer <token>` header this frontend
 * forwards on its behalf.
 */
export const SESSION_COOKIE_NAME = "session";

// Mirrors consumer-api's ACCESS_TOKEN_LIFETIME (auth.py): ~7 days.
const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7;

export interface AccessTokenPayload {
  sub: string;
  iat: number;
  exp: number;
}

/**
 * Decodes a JWT's payload without verifying its signature.
 *
 * The frontend never holds consumer-api's signing secret (JWT_SECRET_KEY) —
 * only consumer-api mints and verifies Access Tokens. This decode is used
 * only for routing decisions (whose session is this, has it expired by its
 * own claim). Any tampering is still caught when consumer-api verifies the
 * token's signature on the next request and rejects with 401.
 */
export function decodeAccessToken(token: string): AccessTokenPayload | null {
  const parts = token.split(".");
  if (parts.length !== 3) {
    return null;
  }

  try {
    const payloadJson = Buffer.from(parts[1], "base64url").toString("utf-8");
    const payload = JSON.parse(payloadJson);
    if (typeof payload.sub !== "string" || typeof payload.exp !== "number") {
      return null;
    }
    return payload as AccessTokenPayload;
  } catch {
    return null;
  }
}

/** True when `token` is a well-formed, non-expired Access Token by its own claim. */
export function isSessionValid(token: string | undefined | null): boolean {
  if (!token) {
    return false;
  }
  const payload = decodeAccessToken(token);
  if (!payload) {
    return false;
  }
  return payload.exp * 1000 > Date.now();
}

export function getSessionToken(request: NextRequest): string | undefined {
  return request.cookies.get(SESSION_COOKIE_NAME)?.value;
}

export interface Session {
  token: string;
  userId: string;
}

/**
 * Reads the Access Token out of this request's own session cookie (never a
 * browser-visible value) and the user id it belongs to. Returns null when
 * there's no usable session — middleware.ts already redirects page
 * navigations without one, but API routes can also be reached directly, so
 * each one checks again rather than trusting the caller.
 */
export function requireSession(request: NextRequest): Session | null {
  const token = getSessionToken(request);
  const payload = token ? decodeAccessToken(token) : null;
  if (!token || !payload) {
    return null;
  }
  return { token, userId: payload.sub };
}

export function setSessionCookie(response: NextResponse, token: string): void {
  response.cookies.set(SESSION_COOKIE_NAME, token, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_MAX_AGE_SECONDS,
  });
}

export function clearSessionCookie(response: NextResponse): void {
  response.cookies.set(SESSION_COOKIE_NAME, "", {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 0,
  });
}
