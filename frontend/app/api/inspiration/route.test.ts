import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SESSION_COOKIE_NAME } from "@/lib/session";

import { POST } from "./route";

function makeInspirationRequest(body: unknown, cookie?: string) {
  return new NextRequest("http://localhost:3000/api/inspiration", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(cookie ? { Cookie: `${SESSION_COOKIE_NAME}=${cookie}` } : {}),
    },
    body: JSON.stringify(body),
  });
}

function makeValidLookingToken(sub = "1"): string {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString(
    "base64url",
  );
  const now = Math.floor(Date.now() / 1000);
  const payload = Buffer.from(
    JSON.stringify({ sub, iat: now, exp: now + 7 * 24 * 60 * 60 }),
  ).toString("base64url");
  return `${header}.${payload}.fake-signature`;
}

describe("POST /api/inspiration", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns 401 and never calls consumer-api when there is no session cookie", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    const response = await POST(makeInspirationRequest({ query: "eggs, flour" }));

    expect(response.status).toBe(401);
    const body = await response.json();
    expect(body.error).toBeTruthy();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns the recipe from consumer-api on success", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          id: "r1",
          name: "Omelette",
          ingredients: ["eggs", "flour"],
          instructions: "Whisk and fry.",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const token = makeValidLookingToken("1");
    const response = await POST(makeInspirationRequest({ query: "eggs, flour" }, token));

    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body.recipe.name).toBe("Omelette");
    expect(body.recipe.ingredients).toEqual(["eggs", "flour"]);

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toContain("/user/1/inspiration");
    expect(options.headers.Authorization).toBe(`Bearer ${token}`);
    expect(JSON.parse(options.body)).toEqual({ query: "eggs, flour" });
  });

  it("surfaces a clear 404 error when consumer-api finds or invents nothing", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ detail: "No recipes found for user_id: 1" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const response = await POST(
      makeInspirationRequest({ query: "mystery paste" }, makeValidLookingToken("1")),
    );

    expect(response.status).toBe(404);
    const body = await response.json();
    expect(body.error).toBeTruthy();
  });
});
