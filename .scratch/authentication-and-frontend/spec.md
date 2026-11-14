# Authentication and Frontend

**Labels**: ready-for-agent
**Status**: draft — issue tracker not yet configured for this repo; run `/setup-matt-pocock-skills` to publish this properly.

## Problem Statement

Right now anyone can call `consumer-api` with any `user_id` in the URL and read or change that user's profile or recipes — there's no concept of logging in, and no check that the caller is who they claim to be. There's also no UI at all: every interaction with the app happens via raw HTTP calls to `consumer-api`.

## Solution

Add password-based login to the platform, enforced at `consumer-api` (the gateway) by issuing and verifying an Access Token for each User, and rejecting any request whose `user_id` doesn't match the token's owner. Add a Next.js frontend that gives people an actual UI for signing up, logging in, managing their profile, managing recipes, and using the "find or invent a recipe" agent flow — all gated behind login.

## User Stories

1. As a visitor, I want to create an account with my name, email, and a password, so that I can start saving my own recipes.
2. As a registered user, I want to be logged in immediately after I sign up, so that I don't have to log in a second time right after registering.
3. As a visitor who already has an account, I want to log in with my email and password, so that I can access my recipes and profile.
4. As a visitor, I want a clear error when I enter the wrong password, so that I know to try again rather than assuming something is broken.
5. As a visitor, I want a clear error when I try to sign up with an email that's already registered, so that I know to log in instead.
6. As a logged-in user, I want my session to stay active for about a week without logging in again, so that I'm not repeatedly interrupted while using the app.
7. As a logged-in user, I want to log out, so that my session ends on the device I'm using.
8. As a visitor who isn't logged in, I want to be redirected to the login page when I try to open any page in the app, so that I never see another user's data by accident.
9. As a logged-in user, I want to only ever see and edit my own profile and my own recipes, so that my data stays private from other users.
10. As a logged-in user, I want a request using someone else's user id to be rejected, so that I can't access another user's recipes or profile even if I guess their id.
11. As a logged-in user, I want to view and update my profile (name, dietary restrictions, preferences) from the frontend, so that I don't need to call the API directly.
12. As a logged-in user, I want to delete my account from the frontend, so that I can remove my data if I no longer want to use the app.
13. As a logged-in user, I want to create a new recipe from the frontend, so that I can save recipes I come up with.
14. As a logged-in user, I want to view a list of my recipes, so that I can browse what I've saved.
15. As a logged-in user, I want to view a single recipe's full details, so that I can read its ingredients and instructions.
16. As a logged-in user, I want to edit an existing recipe, so that I can fix or update it.
17. As a logged-in user, I want to delete a recipe, so that I can remove ones I no longer want.
18. As a logged-in user, I want to enter a list of ingredients and ask the app to find or invent a recipe for me, so that I can figure out what to cook.
19. As a logged-in user, I want the suggested recipe to take my dietary restrictions and preferences into account, so that it's actually something I'd eat.
20. As a logged-in user, I want to see some indication while the recipe-discovery request is processing, so that I know the app is working and not stuck.
21. As a product owner, I want any request with no token, or an invalid/expired token, rejected with 401, so that there's no way to access data without logging in.
22. As a product owner, I want cross-user access attempts rejected with 403 rather than 404, so that it's clear the request was denied rather than the resource not existing.
23. As a developer, I want `recipe-service`, `recipe-embedding-service`, and `discovery-agent-service` left completely unchanged, so that this feature doesn't risk destabilizing services that don't need to know about authentication.
24. As a logged-in user, I want my session to pick up automatically on page refresh as long as my token hasn't expired, so that normal navigation doesn't interrupt my session.
25. As a visitor, I want signing up to require only name, email, and password with no email-verification step, so that I can start using the app immediately.
26. As a user who forgets their password, I want it to be clear there's no self-service reset yet, so that I'm not confused by a missing "forgot password" link.

## Implementation Decisions

**Credential ownership (`user-service`)**
- `User` gains a `password_hash` column. The raw password is never stored or returned by any endpoint.
- Signup (`POST /user`) is extended to accept a `password` field; `user-service` hashes it (bcrypt) before storing.
- A new, internal-only endpoint verifies credentials: given an email and password, it returns the matching `User` on success, or a 401 if the email doesn't exist *or* the password is wrong (same response for both, so the error doesn't reveal which emails are registered). This endpoint is only ever called by `consumer-api`, over the internal Docker network — it is not part of the public API surface.

**Token issuance and enforcement (`consumer-api`)**
- `consumer-api` owns the Access Token entirely: minting it, signing it, and verifying it. `user-service` never sees or creates a token.
- New endpoint `POST /auth/login`: takes `{email, password}`, calls `user-service`'s credential-verification endpoint, and on success mints a JWT (subject = user id, ~7 day expiry) and returns it alongside the user. On failure, returns 401.
- `POST /user` (signup), after creating the user via `user-service`, also mints a token and returns it in the same response — signup auto-logs the user in.
- There is no `/auth/logout` endpoint on `consumer-api`. Per the no-revocation decision, logging out only means discarding the token wherever it's held — which is the frontend's concern, not the gateway's.
- A new auth dependency applies to every route with `user_id` in the path (the existing user profile routes, recipe routes, and the inspiration route): it reads `Authorization: Bearer <token>`, rejects with 401 if missing/invalid/expired, decodes the subject, and rejects with 403 if the subject doesn't match the `user_id` in the path. On success, the route behaves exactly as it does today.
- The JWT signing secret is a new environment variable, following the same pattern as the existing `OPENAI_API_KEY`.

**Frontend (new `frontend/` Next.js app)**
- New top-level `frontend/` directory, own Dockerfile, added to `docker-compose.yml` as a new service pointed at `consumer-api` via a `CONSUMER_API_URL`-style env var, following the existing `*_URL` convention.
- Pages: `/login`, `/signup`, a recipe list/dashboard, a single-recipe view/edit page, a new-recipe page, and an "inspiration" (find-or-invent) page. Every page except `/login` and `/signup` requires a session; its absence redirects to `/login`.
- Server Components fetch data directly from `consumer-api` on the server by default; client components are used only for the login/signup forms and the interactive ingredients-input flow.
- The Access Token exists as an httpOnly, Secure, `SameSite=Lax` cookie — but only between the browser and the Next.js server. It is never exposed to browser-side JS.
- A `POST`-style login route handler on the Next.js server calls `consumer-api`'s `/auth/login`, and on success sets that returned token as the cookie; on failure, it passes the error through to the form.
- A logout route handler simply clears the cookie — it makes no call to `consumer-api`.
- Every other server-side call to `consumer-api` (Server Component data fetches, other route handlers) reads the token out of its own cookie and forwards it as `Authorization: Bearer <token>` — this is the same mechanism a non-browser API client would use directly against `consumer-api`, so nothing about `consumer-api`'s auth dependency is browser-specific.

**Explicitly unchanged**: `recipe-embedding-service`, `discovery-agent-service`, `recipe-mcp-server`, `user-mcp-server`.

**Amendment (post-implementation):** `recipe-service` turned out to need one small additive change after all — there was no way to list a user's recipes anywhere in the stack (only get-by-id/create/update/delete existed), which the recipe list page genuinely requires. A plain `GET /user/{user_id}/recipe` route was added there, matching the existing unauthenticated-internal-route shape of every other route in that file (`consumer-api`'s ownership check is, and remains, the only auth gate). Reviewed and accepted as a necessary gap-fill rather than scope creep.

## Testing Decisions

No automated tests exist anywhere in this repo today — this is the first test suite for any service here, so there's no prior art to follow; the conventions below are being introduced fresh.

A good test here asserts on external behavior — HTTP status codes and response bodies — never on how a password is hashed or how a token is encoded internally.

- **`consumer-api` (seam 1)**: `TestClient` against the FastAPI app, with the `httpx` calls to `user-service`/`recipe-service`/`discovery-agent-service` mocked, so these tests exercise only the gateway's own logic without needing the other services running. Cover: signup success and duplicate-email failure, login success and wrong-password failure, every existing `user_id`-path route returning 401 with no token, 403 with a token for a different user, and 200 (unchanged behavior) with a matching token.
- **`user-service` (seam 2)**: `TestClient` against the FastAPI app with an in-memory SQLite database swapped in through the existing `get_db` dependency override. Cover: the password is hashed (never stored or returned in plaintext) on create, and the new verify-credentials endpoint returns the user on a correct password and 401 on a wrong password or unknown email.
- **Frontend (seam 3)**: server-side tests against the Next.js route handlers (not full browser end-to-end), with `consumer-api` calls mocked. Cover: the login handler sets the cookie on success and surfaces the error on failure, the logout handler clears the cookie, and a request to a protected page with no cookie redirects to `/login`.
- No new tests for `recipe-service`, `recipe-embedding-service`, or `discovery-agent-service` — they're unchanged.

## Out of Scope

- Password reset / forgot-password flow
- Email verification at signup
- OAuth / social login
- Roles or permissions beyond simple per-user ownership
- Refresh tokens or short-lived-token rotation
- Server-side token revocation / logout blocklist
- Public or guest-accessible pages/recipes
- Rate limiting on login or signup
- Any change to `recipe-service`, `recipe-embedding-service`, `discovery-agent-service`, `recipe-mcp-server`, or `user-mcp-server`

## Further Notes

- Password hashing algorithm (bcrypt) wasn't explicitly grilled — it's a standard default with no meaningful trade-off at this project's scale, so it was decided rather than raised as a question.
- Because there's no refresh mechanism and no revocation list, a user logged in on multiple devices will hold independent tokens on each, valid until they individually expire. This is an accepted consequence of the JWT / no-refresh / no-revocation decisions, not a gap to close later.
- Because `consumer-api`'s auth dependency only ever looks at the `Authorization` header — never a cookie — any future non-browser API client can authenticate the same way the frontend's server does, with no changes to `consumer-api`.
