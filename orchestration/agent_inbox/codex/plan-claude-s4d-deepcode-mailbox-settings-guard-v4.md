# Ariadne Conductor Allocation Plan: S4d Refreshed

**Role:** Ariadne Conductor, planning only.
**Date:** 2026-07-11
**Settings fingerprint:** `sha256:cfb5534ea58bb22bdf602ce4f572ea1bc8b68b9ca581f4b4d88d59d060b4a072`
**Supersedes:** V3 only because the complete-settings fingerprint changed.

## Boundary And Allocation

This remains a docs/tests-only guardrail sprint. D1, D2, and D3 are exactly
three DeepSeek Flash/high lanes in separate disposable packet-scoped worktrees:

- D1 owns `tests/test_ariadne_deepcode_adapter_settings.py` and its artifact.
- D2 owns `docs/ariadne-deepcode-adapter-authority.md` and its artifact.
- D3 owns `tests/test_ariadne_deepcode_mailbox_settings.py` and its artifact.

Antigravity/Gemini Flash 3.5 owns an artifact-only veto lane and no source file.
GPT Terra alone integrates, commits, and pushes. No fourth DeepSeek lane is
permitted. If Antigravity is unavailable, record stand-down and use bounded
Ariadne-local review.

## Completion Contract

Each DeepSeek lane requires a durable `DECISION: pass|revision_required`
artifact, one local untrusted PTY adapter event, and one machine-readable
receipt. The PTY adapter fails on permission prompts and may forcibly clean up
only after both a valid artifact and Deep Code turn-completion signal. Terminal
output is not persisted. Events and receipts never substitute for the artifact.

## Gate

No worker dispatch is allowed until a fresh Deep Code verifier artifact for the
fingerprint above returns `DECISION: pass`. Before integration, the protected
orchestrator checks disjoint ownership, three artifacts/events/receipts, and the
Antigravity veto artifact or recorded fallback, then runs the two focused test
files. This plan grants no runtime, provider, frontend, database, GraphQL,
H-series, D5, deployment, release, commit, or push authority to workers.

The Conductor cannot dispatch, alter a verifier-passed allocation, integrate,
commit, or push.
