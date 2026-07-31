# Threat-model delta: Reception One Word Hybrid contextual launch

Recorded: 2026-07-31
Parent: Reception One Bureau post-admission runtime hardening

## New surface

The existing Word taskpane may open the native Diary/Bureau with a typed
in-memory navigation context. This creates a new cross-window message boundary
but no new backend, provider or command authority.

## Threats and controls

| Threat | Control |
|---|---|
| Patient or clinical data leaks through a URL | The Diary URL is unchanged and context-free; patient, appointment, request and token fields are prohibited by schema and tests. |
| A child window treats navigation context as action authority | The contract carries explicit false command/provider/patient-context flags; native code uses it only to navigate and open a read/proposal surface. |
| A crafted message injects fields or an invalid date | Exact allowlist, contract version, type, enum and calendar-date validation; additional fields fail closed. |
| Context and authentication become conflated | Authentication remains the pre-existing separate `auth` message; the launch contract cannot contain credentials or tokens. |
| A stale popup retry changes the requested context | The existing bounded retry reuses the same already-constructed context and does not rebuild from mutable patient state. |
| Reception One opens before the Diary reaches the requested date | Native navigation must return `verified=true` before projection opening for a changed date. |
| A failed contextual launch silently opens another planner or provider | The launch freezes deterministic Standard and grants no provider authority or fallback. |
| A taskpane/Pages source mismatch changes behaviour | Source and `docs/taskpane` copies are synchronized and equality-tested. |
| Protected holdout material influences the implementation after the pre-plan search incident | The printed fixture text is quarantined from reasoning and tests; all implementation evidence is newly authored and explicit-path-only. |

## Preserved controls

- FastAPI/PostgreSQL remain authoritative for Diary truth.
- GraphQL remains read-only.
- Any future scheduling mutation remains an explicit practice-scoped,
  auditable and idempotent REST command with staff confirmation.
- The proofreader remains the sole model-output egress gate.
- Standard remains zero-provider by default.
- No URL-carried PHI, model-to-database write or silent fallback is introduced.

## Residual risk

This tranche can validate the local taskpane and Office-dialog contract using a
stubbed Office host and native-browser evidence. Actual Word Online popup
prompting, tenant policy, focus restoration and cross-window behaviour still
require a later authenticated Word Online exercise. That exercise cannot be
claimed by route-intercepted evidence.
