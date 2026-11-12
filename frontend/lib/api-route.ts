import { NextResponse } from "next/server";

import { ConsumerApiError } from "@/lib/consumer-api";

/** The one 401 response every route returns when `requireSession` finds nothing usable. */
export function unauthorizedResponse(): NextResponse {
  return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
}

/**
 * Runs a route handler body, translating a `ConsumerApiError` into a JSON
 * error response that carries consumer-api's own status code. `toMessage`
 * picks the client-facing message (every route handler used to repeat this
 * same `catch (error) { if (error instanceof ConsumerApiError) {...} throw
 * error; }` shape itself). Any other error rethrows, so Next.js's own
 * handling still applies.
 */
export async function withConsumerApiErrors(
  action: () => Promise<NextResponse>,
  toMessage: (error: ConsumerApiError) => string,
): Promise<NextResponse> {
  try {
    return await action();
  } catch (error) {
    if (error instanceof ConsumerApiError) {
      return NextResponse.json({ error: toMessage(error) }, { status: error.status });
    }
    throw error;
  }
}
