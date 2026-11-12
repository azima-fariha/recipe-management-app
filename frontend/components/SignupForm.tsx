"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

export function SignupForm() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    const formData = new FormData(event.currentTarget);
    const response = await fetch("/api/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: formData.get("full_name"),
        email: formData.get("email"),
        password: formData.get("password"),
      }),
    });

    if (response.ok) {
      // Signup auto-logs the user in.
      router.push("/");
      router.refresh();
      return;
    }

    setSubmitting(false);
    const body = await response.json().catch(() => null);
    setError(body?.error ?? "Something went wrong. Please try again.");
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Sign up</h1>
      {error && <p role="alert">{error}</p>}
      <label>
        Name
        <input name="full_name" type="text" autoComplete="name" required />
      </label>
      <label>
        Email
        <input name="email" type="email" autoComplete="email" required />
      </label>
      <label>
        Password
        <input name="password" type="password" autoComplete="new-password" required />
      </label>
      <button type="submit" disabled={submitting}>
        {submitting ? "Signing up..." : "Sign up"}
      </button>
      <p>
        Already have an account? <a href="/login">Log in</a>
      </p>
      <p>There&apos;s no password reset yet, so hold onto your password.</p>
    </form>
  );
}
