# Recipe Management App

A microservices platform where Users manage Recipes, and an agent discovers or invents Recipes from ingredients.

## Language

**Access Token**:
A signed credential issued to a User at login, proving their identity to consumer-api on later requests. Self-contained (JWT) — consumer-api verifies it without a server-side lookup.
_Avoid_: JWT, session token (those name the encoding, not the concept)

**Ownership**:
The rule that a User may only read or modify Recipes and profile data filed under their own user id. Enforced by rejecting a request when the `user_id` in the URL doesn't match the Access Token's subject.
_Avoid_: Authorization, permission (too broad — Ownership is this app's one specific rule, not a general permission system)
