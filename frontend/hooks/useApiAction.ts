"use client";

import { useState } from "react";

const DEFAULT_ERROR_MESSAGE = "Something went wrong. Please try again.";

export interface RunOptions<T> {
  /** Called with the parsed response body once `perform` resolves with an ok response. */
  onSuccess: (body: T) => void | Promise<void>;
  /** Shown when the response isn't ok and its own body carries no `error` field. */
  fallbackErrorMessage?: string;
}

export interface UseApiActionResult {
  /** True while a call started by `run` is in flight. */
  pending: boolean;
  /** The message from the most recently failed call, or null. */
  error: string | null;
  /**
   * Performs `perform`, parsing its response as JSON (falling back to
   * `null` if the body isn't JSON, e.g. a 204). On a non-ok response, sets
   * `error` to the body's own `error` field, or `fallbackErrorMessage` if
   * it has none. On an ok response, calls `onSuccess` with the parsed body.
   *
   * This is the "loading/error/submit" shape every form and delete-confirm
   * button in this app shares — see components/{LoginForm,SignupForm,
   * ProfileForm,RecipeForm,InspirationForm,DeleteAccountButton,
   * DeleteRecipeButton}.tsx.
   */
  run: <T = unknown>(perform: () => Promise<Response>, options: RunOptions<T>) => Promise<void>;
}

export function useApiAction(): UseApiActionResult {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run<T>(perform: () => Promise<Response>, options: RunOptions<T>) {
    setError(null);
    setPending(true);
    try {
      const response = await perform();
      const body = await response.json().catch(() => null);
      if (!response.ok) {
        setError(
          (body as { error?: string } | null)?.error ??
            options.fallbackErrorMessage ??
            DEFAULT_ERROR_MESSAGE,
        );
        return;
      }
      await options.onSuccess(body as T);
    } finally {
      setPending(false);
    }
  }

  return { pending, error, run };
}
