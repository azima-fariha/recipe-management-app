"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

interface ProfileFormProps {
  initialFullName: string | null;
  initialDietaryRestrictions: string | null;
  initialPreferences: string | null;
}

export function ProfileForm({
  initialFullName,
  initialDietaryRestrictions,
  initialPreferences,
}: ProfileFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(false);
    setSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const response = await fetch("/api/profile", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: formData.get("full_name"),
        dietary_restrictions: formData.get("dietary_restrictions"),
        preferences: formData.get("preferences"),
      }),
    });

    setSubmitting(false);

    if (response.ok) {
      setSuccess(true);
      router.refresh();
      return;
    }

    const body = await response.json().catch(() => null);
    setError(body?.error ?? "Something went wrong. Please try again.");
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <p role="alert">{error}</p>}
      {success && <p role="status">Profile updated.</p>}
      <label>
        Name
        <input name="full_name" defaultValue={initialFullName ?? ""} required />
      </label>
      <label>
        Dietary restrictions
        <textarea name="dietary_restrictions" defaultValue={initialDietaryRestrictions ?? ""} />
      </label>
      <label>
        Preferences
        <textarea name="preferences" defaultValue={initialPreferences ?? ""} />
      </label>
      <button type="submit" disabled={submitting}>
        {submitting ? "Saving..." : "Save changes"}
      </button>
    </form>
  );
}
