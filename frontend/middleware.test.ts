import { NextRequest } from "next/server";
import { describe, expect, it } from "vitest";

import { SESSION_COOKIE_NAME } from "@/lib/session";

import { middleware } from "./middleware";

function makeExpiredToken(): string {
  const header = Buffer.from(JSON.stringify({ alg: "HS256", typ: "JWT" })).toString(
    "base64url",
  );
  const now = Math.floor(Date.now() / 1000);
  const payload = Buffer.from(
    JSON.stringify({ sub: "1", iat: now - 8 * 24 * 60 * 60, exp: now - 24 * 60 * 60 }),
  ).toString("base64url");
  return `${header}.${payload}.fake-signature`;
}

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

describe("middleware", () => {
  it("redirects a protected-page request with no cookie to /login", () => {
    const request = new NextRequest("http://localhost:3000/");

    const response = middleware(request);

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("http://localhost:3000/login");
  });

  it("redirects a protected-page request with an expired cookie to /login", () => {
    const request = new NextRequest("http://localhost:3000/", {
      headers: { Cookie: `${SESSION_COOKIE_NAME}=${makeExpiredToken()}` },
    });

    const response = middleware(request);

    expect(response.status).toBe(307);
    expect(response.headers.get("location")).toBe("http://localhost:3000/login");
  });

  it("passes through a protected-page request with a valid-looking cookie", () => {
    const request = new NextRequest("http://localhost:3000/", {
      headers: { Cookie: `${SESSION_COOKIE_NAME}=${makeValidLookingToken()}` },
    });

    const response = middleware(request);

    expect(response.status).toBe(200);
    expect(response.headers.get("location")).toBeNull();
  });

  it("does not redirect requests to /login itself, even with no cookie", () => {
    const request = new NextRequest("http://localhost:3000/login");

    const response = middleware(request);

    expect(response.status).toBe(200);
    expect(response.headers.get("location")).toBeNull();
  });

  it("does not redirect requests to /signup itself, even with no cookie", () => {
    const request = new NextRequest("http://localhost:3000/signup");

    const response = middleware(request);

    expect(response.status).toBe(200);
    expect(response.headers.get("location")).toBeNull();
  });
});
