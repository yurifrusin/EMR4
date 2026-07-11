# Deep Code S4d Verifier Packet

Date: 2026-07-11

## Role

You are the Ariadne verifier. Return exactly one durable Markdown review artifact
at `orchestration/agent_inbox/codex/review-deepcode-s4d-adapter-settings-guard.md`.
The first decision line must be either `DECISION: pass` or
`DECISION: revision_required`.

Do not edit any other file, dispatch workers, change settings, commit, push, or
claim integration authority. Deep Code permission approval is local tool
permission only and does not change this role boundary.

## Current Settings Facts

- Head and handoff used by the Conductor: `57fe65e8`.
- Deep Code is an interactive real-TTY transport. Its default is
  `deepseek-v4-flash` with `high` reasoning.
- `deepseek-v4-pro` and `max` reasoning are exceptional choices requiring a
  recorded leverage reason.
- A non-TTY refusal is current-surface adapter unavailability, not DeepSeek
  unavailability.
- A durable worker artifact is required before an outcome is accepted.
- The conductor and verifier cannot integrate, commit, or push. GPT Terra is
  the protected orchestrator and sole integrator.
- DeepSeek lanes must be between one and three, with distinct packet ownership.

## Conductor Plan To Verify

**Objective:** add only two new docs/tests artifacts that mechanically guard the
Deep Code adapter settings against drift. No runtime, provider, frontend,
database, GraphQL, H15/H-series, D5, deployment, or settings-value changes.

**Lane D1:** `tests/test_ariadne_deepcode_adapter_settings.py` only. It checks
the Deep Code model profile default, exceptional model/reasoning policy,
interactive-TTY and non-TTY posture, durable-artifact completion contract,
adapter resource mapping, and permission-versus-authority rule. It also includes
one in-memory negative test.

**Lane D2:** `docs/ariadne-deepcode-adapter-authority.md` only. It documents
reachability versus authority, non-TTY handling, permission prompts, and durable
artifact completion.

**Antigravity:** one independent review artifact only, no source edits.

**Checks after integration:** focused new pytest, full `pytest tests -q`,
`git diff --check`, manual doc/settings consistency read.

## Required Review

Decide whether the plan complies with the above settings and authority split.
List concrete blocking reasons if it does not. Do not accept the plan merely
because the Deep Code smoke passed.
