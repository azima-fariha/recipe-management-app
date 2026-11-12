import { NextRequest } from "next/server";
import { describe, expect, it } from "vitest";

import { SESSION_COOKIE_NAME } from "@/lib/session";

import { POST } from "./route";

describe("POST /api/auth/logout", () => {
  it("clears the session cookie", async () => {
    const request = new NextRequest("http://localhost:3000/api/auth/logout", {
      method: "POST",
      headers: { Cookie: `${SESSION_COOKIE_NAME}=a.jwt.token` },
    });

    const response = await POST(request);

    expect(response.status).toBe(200);
    const cleared = response.cookies.get(SESSION_COOKIE_NAME);
    expect(cleared?.value).toBe("");
    expect(cleared?.maxAge).toBe(0);
  });
});
