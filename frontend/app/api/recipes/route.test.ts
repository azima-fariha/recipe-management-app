import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SESSION_COOKIE_NAME } from "@/lib/session";

import { POST } from "./route";

function makeToken(sub: string): string {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString(
    "base64url",
  );
  const now = Math.floor(Date.now() / 1000);
  const payload = Buffer.from(
    JSON.stringify({ sub, iat: now, exp: now + 7 * 24 * 60 * 60 }),
  ).toString("base64url");
  return `${header}.${payload}.fake-signature`;
}

function makeCreateRequest(body: unknown, token?: string) {
  return new NextRequest("http://localhost:3000/api/recipes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Cookie: `${SESSION_COOKIE_NAME}=${token}` } : {}),
    },
    body: JSON.stringify(body),
  });
}

describe("POST /api/recipes", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("creates the recipe for the session's own user and returns it", async () => {
    const token = makeToken("1");
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ id: "abc", name: "Soup", ingredients: ["water"], instructions: "Boil" }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const response = await POST(
      makeCreateRequest({ name: "Soup", ingredients: ["water"], instructions: "Boil" }, token),
    );

    expect(response.status).toBe(201);
    const body = await response.json();
    expect(body.recipe.id).toBe("abc");

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://localhost:8088/user/1/recipe");
    expect(init.headers.Authorization).toBe(`Bearer ${token}`);
  });

  it("rejects with 401 when there is no session cookie", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    const response = await POST(
      makeCreateRequest({ name: "Soup", ingredients: ["water"], instructions: "Boil" }),
    );

    expect(response.status).toBe(401);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
