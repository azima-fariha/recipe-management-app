import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SESSION_COOKIE_NAME } from "@/lib/session";

import { POST } from "./route";

function makeSignupRequest(body: unknown) {
  return new NextRequest("http://localhost:3000/api/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

describe("POST /api/auth/signup", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sets the session cookie and returns the user on success (auto-login)", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          access_token: "a.jwt.token",
          token_type: "bearer",
          user: { id: 1, full_name: "Ada Lovelace", email: "ada@example.com" },
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const response = await POST(
      makeSignupRequest({
        full_name: "Ada Lovelace",
        email: "ada@example.com",
        password: "s3cr3t-pass",
      }),
    );

    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.user.email).toBe("ada@example.com");

    const setCookie = response.cookies.get(SESSION_COOKIE_NAME);
    expect(setCookie?.value).toBe("a.jwt.token");
    expect(setCookie?.httpOnly).toBe(true);
    expect(setCookie?.secure).toBe(true);
    expect(setCookie?.sameSite).toBe("lax");
  });

  it("surfaces a clear error and sets no cookie on a duplicate email", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Email is already registered" }), {
        status: 409,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const response = await POST(
      makeSignupRequest({
        full_name: "Ada Lovelace",
        email: "ada@example.com",
        password: "s3cr3t-pass",
      }),
    );

    expect(response.status).toBe(409);
    const body = await response.json();
    expect(body.error).toBeTruthy();
    expect(response.cookies.get(SESSION_COOKIE_NAME)).toBeUndefined();
  });
});
