# 02: Frontend shell — login, signup, session, protected home

**What to build:** The new Next.js frontend exists and is wired into the stack. A visitor can sign up or log in, lands on a protected home page, and gets redirected back to login if they're not signed in. The session lives as an httpOnly cookie that only the frontend's own server ever touches — the browser never holds the raw token, and `consumer-api` only ever sees a plain `Authorization: Bearer` header.

**Blocked by:** 01 (auth backend)

**Status:** ready-for-agent

- [ ] A new `frontend/` Next.js app is added as a service in `docker-compose.yml`, pointed at `consumer-api` via an env var following the existing `*_URL` convention
- [ ] `/signup` and `/login` pages exist; a successful submission sets an httpOnly, Secure, `SameSite=Lax` session cookie and lands on the home page
- [ ] A clear error is shown for wrong password (login) and for a duplicate email (signup)
- [ ] A protected home page exists (placeholder content is fine) and redirects to `/login` when there's no valid session
- [ ] Logging out clears the cookie and returns to `/login`
- [ ] Every server-side call from the frontend to `consumer-api` reads the token from the cookie and forwards it as `Authorization: Bearer <token>` — `consumer-api` requires no cookie support of its own
