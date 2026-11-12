import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/LogoutButton";
import { ConsumerApiError, fetchUser } from "@/lib/consumer-api";
import { decodeAccessToken, SESSION_COOKIE_NAME } from "@/lib/session";

// Protected home page (placeholder). Route protection itself is enforced by
// middleware.ts; this component additionally redirects if the token turns
// out to be rejected by consumer-api (e.g. tampered or revoked at the
// gateway), since the frontend can only check the token's own claims, not
// verify its signature (only consumer-api holds JWT_SECRET_KEY).
export default async function HomePage() {
  const token = cookies().get(SESSION_COOKIE_NAME)?.value;
  const payload = token ? decodeAccessToken(token) : null;

  if (!token || !payload) {
    redirect("/login");
  }

  let user;
  try {
    user = await fetchUser(payload.sub, token);
  } catch (error) {
    if (error instanceof ConsumerApiError && (error.status === 401 || error.status === 403)) {
      redirect("/login");
    }
    throw error;
  }

  return (
    <main>
      <h1>Welcome, {user.full_name ?? user.email}</h1>
      <p>
        <a href="/inspiration">Find or invent a recipe from ingredients</a>
      </p>
      <LogoutButton />
    </main>
  );
}
