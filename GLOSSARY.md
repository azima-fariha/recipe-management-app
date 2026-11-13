# Recipe Management App

A microservices platform where Users manage Recipes, and an agent discovers or invents Recipes from ingredients.

## Language

**Access Token**:
A signed credential issued to a User at login, proving their identity to consumer-api on later requests. Self-contained (JWT) — consumer-api verifies it without a server-side lookup.
_Avoid_: JWT, session token (those name the encoding, not the concept)

**Ownership**:
The rule that a User may only read or modify Recipes and profile data filed under their own user id. Enforced by rejecting a request when the `user_id` in the URL doesn't match the Access Token's subject.
_Avoid_: Authorization, permission (too broad — Ownership is this app's one specific rule, not a general permission system)

**Hallucination** (invented-recipe path only):
An invented recipe that either violates the User's stated dietary restrictions, or is structurally nonsensical/unsafe (a dangerous or incoherent ingredient combination). There is no ground-truth text to diff against for an invented recipe, so this is the project's operational definition rather than the general "unsupported claim" sense of the word.
_Avoid_: using this term for the found-recipe path — there, the relevant failure is a grounding/faithfulness problem (the agent returning a found recipe inaccurately), not a hallucination
