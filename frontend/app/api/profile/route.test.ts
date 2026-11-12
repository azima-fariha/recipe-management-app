import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SESSION_COOKIE_NAME } from "@/lib/session";

import { DELETE, PUT } from "./route";

// Same construction as middleware.test.ts's makeValidLookingToken: a
// well-formed, non-expired JWT by its own claim. Fine for this seam since
// route handlers never verify the signature themselves — only consumer-api
// does, by checking the forwarded Authorization header.
function makeValidLookingToken(): string {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString(
    "base64url",
  );
  const now = Math.floor(Date.now() / 1000);
  const payload = Buffer.from(
    JSON.stringify({ sub: "1", iat: now, exp: now + 7 * 24 * 60 * 60 }),
  ).toString("base64url");
  return `${header}.${payload}.fake-signature`;
}

function makeProfileRequest(
  method: "PUT" | "DELETE",
  options: { body?: unknown; cookie?: string } = {},
) {
  const headers: Record<string, string> = {};
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (options.cookie) {
    headers["Cookie"] = options.cookie;
  }

  return new NextRequest("http://localhost:3000/api/profile", {
    method,
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });
}

describe("PUT /api/profile", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("rejects a request with no session cookie", async () => {
    const response = await PUT(makeProfileRequest("PUT", { body: { full_name: "Ada L." } }));

    expect(response.status).toBe(401);
  });

  it("forwards the session's Access Token and returns the updated fields on success", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          full_name: "Ada L.",
          dietary_restrictions: "vegetarian",
          preferences: "spicy",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    const token = makeValidLookingToken();

    const response = await PUT(
      makeProfileRequest("PUT", {
        body: { full_name: "Ada L.", dietary_restrictions: "vegetarian", preferences: "spicy" },
        cookie: `${SESSION_COOKIE_NAME}=${token}`,
      }),
    );

    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.user.full_name).toBe("Ada L.");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.method).toBe("PUT");
    expect(init.headers.Authorization).toBe(`Bearer ${token}`);
  });

  it("passes through consumer-api's error status on failure", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "Token does not grant access to this user" }), {
        status: 403,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const response = await PUT(
      makeProfileRequest("PUT", {
        body: { full_name: "Ada L." },
        cookie: `${SESSION_COOKIE_NAME}=${makeValidLookingToken()}`,
      }),
    );

    expect(response.status).toBe(403);
    const body = await response.json();
    expect(body.error).toBeTruthy();
  });
});

describe("DELETE /api/profile", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("rejects a request with no session cookie", async () => {
    const response = await DELETE(makeProfileRequest("DELETE"));

    expect(response.status).toBe(401);
  });

  it("deletes the account, clears the session cookie, and returns ok on success", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);
    const token = makeValidLookingToken();

    const response = await DELETE(
      makeProfileRequest("DELETE", {
        cookie: `${SESSION_COOKIE_NAME}=${token}`,
      }),
    );

    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.ok).toBe(true);

    const setCookie = response.cookies.get(SESSION_COOKIE_NAME);
    expect(setCookie?.value).toBe("");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.method).toBe("DELETE");
    expect(init.headers.Authorization).toBe(`Bearer ${token}`);
  });

  it("passes through consumer-api's error status and does not clear the cookie on failure", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "nope" }), { status: 403 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const response = await DELETE(
      makeProfileRequest("DELETE", {
        cookie: `${SESSION_COOKIE_NAME}=${makeValidLookingToken()}`,
      }),
    );

    expect(response.status).toBe(403);
    const body = await response.json();
    expect(body.error).toBeTruthy();
    expect(response.cookies.get(SESSION_COOKIE_NAME)).toBeUndefined();
  });
});
