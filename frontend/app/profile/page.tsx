import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { DeleteAccountButton } from "@/components/DeleteAccountButton";
import { ProfileForm } from "@/components/ProfileForm";
import { ConsumerApiError, fetchUser } from "@/lib/consumer-api";
import { decodeAccessToken, SESSION_COOKIE_NAME } from "@/lib/session";

// Protected profile page. Route protection itself is enforced by
// middleware.ts; this component additionally redirects if the token turns
// out to be rejected by consumer-api (e.g. tampered or expired at the
// gateway), mirroring the home page's handling.
export default async function ProfilePage() {
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
      <h1>Your profile</h1>
      <p>{user.email}</p>
      <ProfileForm
        initialFullName={user.full_name}
        initialDietaryRestrictions={user.dietary_restrictions ?? null}
        initialPreferences={user.preferences ?? null}
      />
      <DeleteAccountButton />
      <p>
        <a href="/">Back home</a>
      </p>
    </main>
  );
}
