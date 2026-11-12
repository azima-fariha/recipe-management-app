import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SESSION_COOKIE_NAME } from "@/lib/session";

import { DELETE, PUT } from "./route";

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

function makeRequest(method: string, body: unknown, token?: string) {
  return new NextRequest("http://localhost:3000/api/recipes/abc", {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Cookie: `${SESSION_COOKIE_NAME}=${token}` } : {}),
    },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  });
}

const params = { params: { id: "abc" } };

describe("PUT /api/recipes/[id]", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("updates the recipe for the session's own user and returns it", async () => {
    const token = makeToken("1");
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ id: "abc", name: "Soup v2", ingredients: ["water"], instructions: "Boil" }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const response = await PUT(makeRequest("PUT", { name: "Soup v2" }, token), params);

    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.recipe.name).toBe("Soup v2");

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://localhost:8088/user/1/recipe/abc");
    expect(init.headers.Authorization).toBe(`Bearer ${token}`);
  });

  it("rejects with 401 when there is no session cookie", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    const response = await PUT(makeRequest("PUT", { name: "Soup v2" }), params);

    expect(response.status).toBe(401);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe("DELETE /api/recipes/[id]", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("deletes the recipe for the session's own user", async () => {
    const token = makeToken("1");
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    const response = await DELETE(makeRequest("DELETE", undefined, token), params);

    expect(response.status).toBe(200);

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("http://localhost:8088/user/1/recipe/abc");
    expect(init.method).toBe("DELETE");
    expect(init.headers.Authorization).toBe(`Bearer ${token}`);
  });

  it("rejects with 401 when there is no session cookie", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    const response = await DELETE(makeRequest("DELETE", undefined), params);

    expect(response.status).toBe(401);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
