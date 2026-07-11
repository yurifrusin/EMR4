# Review: Deep Code S4d Mailbox + Adapter Settings Guard

**Verifier:** Deep Code (ariadne-verifier role)
**Date:** 2026-07-11
**Conductor Settings Fingerprint:** `d5e91fee`

## DECISION: revision_required

## Plan Summary (as stated)

- **Boundary:** docs/tests-only guardrail sprint. No runtime, provider, frontend, DB, GraphQL, H15/H-series, D5, deployment, release, or settings-value work.
- **D1:** `tests/test_ariadne_deepcode_adapter_settings.py` — pins model, reasoning, TTY/non-TTY, durable artifact, and permission-authority settings (one negative test).
- **D2:** `docs/ariadne-deepcode-adapter-authority.md` — documents reachability vs authority, non-TTY handling, permissions, and artifacts.
- **D3:** `tests/test_ariadne_deepcode_mailbox_settings.py` — pins mailbox local-only/outbox trust and strict capability settings (one negative test).
- **Antigravity:** review/veto artifact only, no source edits.
- All three DeepSeek lanes use separate fresh TTY sessions with disjoint file ownership.

## Issues Found

### 1. Lane-count fallback exceeds the one-to-three limit

The Conductor states: *"if Antigravity fails it could substitute a **fourth** DeepSeek review lane."*

Settings facts require that **DeepSeek worker lanes must remain within the declared one-to-three limit** (the `deepseek-flash-workers` pool). D1, D2, and D3 already consume three DeepSeek lanes, which is the maximum. Adding a fourth substitutes one lane type (Antigravity) with another (DeepSeek) without dropping an existing DeepSeek lane, producing **four** DeepSeek lanes total — a conflict with the lane-count policy.

**Required revision:** Remove or rephrase the fourth-lane fallback. The allowed options are:
- If Antigravity fails, stand down the Antigravity lane entirely and distribute its review/veto scope across existing DeepSeek lanes or fold it into Ariadne's integration pass.
- If Antigravity fails, substitute a non-DeepSeek lane (e.g., a bounded Ariadne-local review) instead of creating a fourth DeepSeek worker.

## Items That Pass

| Check | Result | Notes |
|---|---|---|
| **Scope boundary** | Pass | docs/tests-only; no runtime/provider/frontend/DB/GraphQL/H15/D5/deployment/release work. |
| **Authority split** | Pass | D1 (tests), D2 (docs), D3 (tests) have disjoint file ownership. Antigravity is review-only. |
| **Artifact + mailbox requirement** | Pass | D3 tests mailbox trust and strict capability. D2 documents authority. The outbox is correctly treated as untrusted. |
| **Permission profile** | Pass | `askAll` with pre-allowed read/worktree and Git-log queries; writes require packet scope. |
| **Integration authority** | Pass | Only GPT Terra orchestrator integrates/commits/pushes — correctly preserved. |
| **Antigravity veto surface** | Pass | Review/veto artifact is a distinct integrable surface. No source edits from Antigravity. |
| **TTY separation** | Pass | All lanes use separate fresh TTY sessions. |

## Verdict

The plan is structurally sound except for the lane-count fallback conflict. Revise the Antigravity substitution clause to stay within the one-to-three DeepSeek lane limit, then re-verify.

## Role Boundary Affirmation

This verification artifact was authored by the Ariadne verifier role. No other files were edited, no commands run, no workers dispatched, no settings changed, and no integration, commit, or push authority was exercised.
