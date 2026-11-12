"use client";

import { useRouter } from "next/navigation";
import { type FormEvent } from "react";

import { useApiAction } from "@/hooks/useApiAction";

export function LoginForm() {
  const router = useRouter();
  const { pending, error, run } = useApiAction();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);

    await run(
      () =>
        fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: formData.get("email"),
            password: formData.get("password"),
          }),
        }),
      {
        onSuccess: () => {
          router.push("/");
          router.refresh();
        },
      },
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <h1>Log in</h1>
      {error && <p role="alert">{error}</p>}
      <label>
        Email
        <input name="email" type="email" autoComplete="email" required />
      </label>
      <label>
        Password
        <input name="password" type="password" autoComplete="current-password" required />
      </label>
      <button type="submit" disabled={pending}>
        {pending ? "Logging in..." : "Log in"}
      </button>
      <p>
        No account yet? <a href="/signup">Sign up</a>
      </p>
    </form>
  );
}
