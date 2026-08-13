# Visible native Diary status-confirm wiring threat-model delta

**Date:** 2026-08-13
**Timestamp:** 2026-08-13T15:13:59+10:00 (Australia/Brisbane)
**Status:** Frozen
**Parent authority:** accepted status-confirm backend and ordinary/fallback
Diary client contracts

## Changed surface

This tranche changes only how an existing staff status command is presented
and announced by the native Diary. The server remains the sole owner of
current authority, current database truth, warning admission, idempotency,
audit and commit.

## Threats and required controls

| Threat | Required control |
|---|---|
| A changed selector appears committed before the backend accepts it | Treat the selected value as a proposal, disable it while pending, reload authoritative truth after success, and restore the prior value on every non-commit path. |
| A stale proposal is treated as write authority | Carry only the accepted signed proposal evidence and let status-confirm recheck current authority and Diary truth. Display failure as “not changed”; never retry through a raw route. |
| A routine transition gains confirmation fatigue | Preserve the accepted no-extra-dialog path for safe non-terminal changes. Require explicit confirmation only for warnings, proposal-tier or terminal changes. |
| Keyboard or assistive-technology users accidentally confirm | Use a labelled/described modal, focus containment, Escape-to-cancel, explicit buttons and focus restoration. No implicit Enter shortcut is introduced. |
| Failure, cancellation or interruption leaves an ambiguous UI state | Clear busy state in `finally`, restore the previous visible status, announce the non-change, and offer no optimistic success state. |
| Status feedback leaks patient details | Keep the transaction status line administrative and status-only; do not copy proposal payloads, identifiers or patient names into it. |
| Browser proof is mistaken for live product integration | Use authored-synthetic fixtures and label network-intercepted evidence `route_intercepted_browser`. Inherit backend route proof separately. |
| Scope expands into a new command or client | Reject new routes, raw writes, GraphQL mutations, external patient channels, providers, credentials, database/source access, deployment and release. |

## Residual boundary

The UI cannot make a stale selection safe. Correctness continues to come from
the backend command's atomic current-authority and current-truth recheck. Event
cues may later accelerate refresh, but they are not command evidence. Restart,
unknown-commit and durable event/cue delivery remain outside this tranche.
