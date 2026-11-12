# 01: Auth backend — signup, login, ownership enforcement

**What to build:** `user-service` stores a hashed password for each User and can verify credentials against it. `consumer-api` issues an Access Token on signup (signing up logs you in immediately) and on login, and now requires a valid, matching token on every existing `/user/{user_id}/...` route — the user, recipe, and inspiration routes alike.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] `POST /user` (signup) accepts a password, stores only a bcrypt hash of it (never the plaintext, never returned by any endpoint), and returns an access token alongside the created user
- [ ] A new, internal-only `user-service` endpoint verifies an email+password pair and returns the matching user on success; returns the same error for "unknown email" and "wrong password" so neither leaks which emails are registered
- [ ] `POST /auth/login` on `consumer-api` accepts `{email, password}`, calls the verification above, and returns an access token on success or 401 on failure
- [ ] Every existing route with `user_id` in the path (`/user/{user_id}`, `/user/{user_id}/recipe/...`, `/user/{user_id}/inspiration`) returns 401 when the request has no token, or an invalid/expired one
- [ ] Every such route returns 403 when the token's subject doesn't match the `user_id` in the path
- [ ] Existing behavior (200/404/etc.) is unchanged when the token is valid and matches the path's `user_id`
- [ ] `recipe-service`, `recipe-embedding-service`, and `discovery-agent-service` are untouched
