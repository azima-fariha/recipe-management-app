"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function DeleteAccountButton() {
  const router = useRouter();
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleDelete() {
    setError(null);
    const response = await fetch("/api/profile", { method: "DELETE" });

    if (response.ok) {
      // The route handler already cleared the session cookie; this ends
      // the session on the device the user is using.
      router.push("/login");
      router.refresh();
      return;
    }

    const body = await response.json().catch(() => null);
    setError(body?.error ?? "Could not delete account. Please try again.");
  }

  if (!confirming) {
    return <button onClick={() => setConfirming(true)}>Delete account</button>;
  }

  return (
    <div>
      {error && <p role="alert">{error}</p>}
      <p>Are you sure? This can&apos;t be undone.</p>
      <button onClick={handleDelete}>Yes, delete my account</button>
      <button onClick={() => setConfirming(false)}>Cancel</button>
    </div>
  );
}
