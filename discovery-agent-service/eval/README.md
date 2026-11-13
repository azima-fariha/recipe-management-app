# Agent Evaluation Harness

Offline evaluation for `discovery-agent-service`'s RAG (find) and agentic (invent) paths.
A custom script, not a framework — see `GLOSSARY.md` for the project's definition of
**Hallucination** on the invented-recipe path. This shape (custom script over RAGAS/DeepEval,
one-off run over CI, offline-only over a runtime guardrail) was settled via a `/grill-with-docs`
session rather than specced/ticketed — small enough in scope to go straight to `/implement`.

## Running it

Requires the full stack up (`docker compose up --build` from the repo root) and
`OPENAI_API_KEY` set in the root `.env` — this harness makes real OpenAI calls, both through
the agent under test and through its own judge.

```bash
cd discovery-agent-service/eval
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python run.py
```

It seeds two fresh eval users through the real signup/login/recipe-create flow (exercising
real auth, not a shortcut), runs 15 golden-set cases against the real stack, and writes a
markdown report to `results/<timestamp>.md` (gitignored — it's a point-in-time artifact, not
source). Exits non-zero if any case failed, for scripting convenience; nothing is gated on
this in CI, since there is no CI in this repo.

## What's covered

| Category | Mechanism | Cases |
|---|---|---|
| Retrieval | Deterministic: exact diff against the actual seeded recipe | 2 |
| Cross-user isolation | Deterministic: confirms the Qdrant `user_id` filter holds | 2 |
| Hallucination (invent path) | `gpt-4.1` judge + ingredient denylist backstop | 2 |
| Judge calibration | Proves the judge itself catches a known violation and passes a known-safe case | 2 |
| Denylist calibration | Proves the denylist backstop catches an outright toxic ingredient | 1 |
| Adversarial | Fake ingredients, off-topic injection, `user_id` smuggling | 3 |
| Robustness | Empty input, phrasing variance, an unusually long ingredient list | 3 |

Retrieval and groundedness are deterministic because real ground truth exists (the actual
seeded recipe); refusal correctness is deterministic because the agent's own system prompt
defines the refusal shape (empty `ingredients`, a non-empty explanation). Only the invented
path's constraint-adherence check genuinely needs judgment, which is why it's the one metric
with an LLM judge — see the grilling session for the full reasoning on each choice.

## Known finding: empty input causes a hallucination, not a refusal

The one case this harness does **not** make pass: `robustness-empty-query`. Sending an empty
`query` string doesn't trigger a refusal — the agent confidently invents a full recipe (e.g.
"Classic Tomato Pasta") from nothing.

This isn't a harness bug; it's left as a genuine finding rather than patched, consistent with
this feature's scope (offline eval only, no runtime guardrail — see the grilling session,
round 1). The system prompt's refusal guideline ("reject non-real ingredients") doesn't
explicitly cover the *absence* of ingredients, which is a distinct case from a fake one. The
natural fix — out of scope here — would be either a prompt addition ("if no ingredients are
given at all, ask for clarification instead of inventing") or a cheap pre-check in
`consumer-api`/`discovery-agent-service` rejecting an empty query before it ever reaches the
agent.
