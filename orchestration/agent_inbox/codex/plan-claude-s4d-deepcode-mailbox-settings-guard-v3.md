# Ariadne Conductor Allocation Plan: S4d Deep Code Adapter/Mailbox Settings Guard

**Role:** Ariadne Conductor, planning only.
**Date:** 2026-07-11
**Settings fingerprint:** `sha256:f52d391472d9fb0e361d1bef9b840bbcad9a028e4ebae56e2e2401bc6edbc61f`
**Supersedes:** the V2 plan rejected for proposing a fourth DeepSeek lane.

## Boundary

This is a docs/tests-only guardrail sprint. It does not change runtime behavior,
providers, frontend code, database, GraphQL, H15/H-series, D5, deployment,
release, telemetry, or committed settings values.

## Allocation

| Lane | Resource | Model / reasoning | Owns |
| --- | --- | --- | --- |
| D1 | DeepSeek worker lane 1, fresh Deep Code TTY | `deepseek-v4-flash` / high | `tests/test_ariadne_deepcode_adapter_settings.py` |
| D2 | DeepSeek worker lane 2, fresh Deep Code TTY | `deepseek-v4-flash` / high | `docs/ariadne-deepcode-adapter-authority.md` |
| D3 | DeepSeek worker lane 3, fresh Deep Code TTY | `deepseek-v4-flash` / high | `tests/test_ariadne_deepcode_mailbox_settings.py` |
| Veto | Antigravity / Gemini Flash 3.5 | medium | durable review/veto artifact only; no source edits |
| Integration | protected GPT Terra orchestrator | high | integration, commit, and push only |

The three DeepSeek lanes exactly fill the declared one-to-three cap. Each runs
in a distinct disposable packet-scoped worktree. No worker can change the
allocation, integrate, commit, or push.

## Packet Requirements

- D1 pins model/reasoning defaults, real-TTY requirement, non-TTY adapter
  evidence, durable-artifact authority, and permission-is-not-authority rules,
  including a negative test.
- D2 documents reachability versus authority, non-TTY handling, permission
  scope, disposable-worktree containment, and durable-artifact requirements.
- D3 pins local-only/untrusted mailbox semantics, denied capabilities, cwd-wide
  write containment, and semantic-not-CLI packet scope, including a negative
  test.

For every DeepSeek lane, completion requires both a durable packet artifact and
a local notify-outbox event. The event is untrusted and never substitutes for
the artifact. A pre-authorized Deep Code `write-in-cwd` permission covers its
entire process cwd, not just the outbox; therefore packet scope is semantic and
every worker must use a disposable packet-scoped worktree.

## Antigravity Fallback

If Antigravity is unavailable or does not provide a durable artifact, either
stand its lane down with the reason recorded or use a bounded Ariadne-local
integration review. A fourth DeepSeek lane is prohibited under every fallback.
Standing Antigravity down is reduced independent review and must be recorded.

## Verification And Gate

Before integration, the protected orchestrator checks ownership boundaries,
three DeepSeek durable artifacts plus three outbox events, the Antigravity veto
artifact or recorded fallback, and runs:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_deepcode_mailbox_settings.py -q
```

No D1/D2/D3 or Antigravity worker may be dispatched until the fresh Deep Code
verifier artifact for this fingerprint returns `DECISION: pass`.

## Role Affirmation

The Conductor cannot dispatch workers, alter a verifier-passed allocation,
integrate, commit, or push. This artifact records a plan only.
