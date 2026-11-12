"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { useApiAction } from "@/hooks/useApiAction";

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
  const [success, setSuccess] = useState(false);
  const { pending, error, run } = useApiAction();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSuccess(false);

    const formData = new FormData(event.currentTarget);

    await run(
      () =>
        fetch("/api/profile", {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            full_name: formData.get("full_name"),
            dietary_restrictions: formData.get("dietary_restrictions"),
            preferences: formData.get("preferences"),
          }),
        }),
      {
        onSuccess: () => {
          setSuccess(true);
          router.refresh();
        },
      },
    );
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
      <button type="submit" disabled={pending}>
        {pending ? "Saving..." : "Save changes"}
      </button>
    </form>
  );
}
