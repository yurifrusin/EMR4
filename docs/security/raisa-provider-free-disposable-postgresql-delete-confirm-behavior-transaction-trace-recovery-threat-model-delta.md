# Delete-confirm behavior/transaction trace-recovery threat-model delta

Date: 2026-08-16

Timestamp: 2026-08-16T13:09:34.9753447+10:00 (Australia/Brisbane)

Status: `frozen_provider_free_trace_recovery_delta`

This delta narrows AER-0352 diagnosis. All controls from the parent behavior
plan and physical scaffold remain in force.

| Threat | Failure mode | Required control |
|---|---|---|
| `DCTR-001` | Diagnostic evidence leaks SQL, parameters or synthetic row values | Persist only closed group/outcome enums and the six existing value-free statement tokens; schema rejects all extra keys and raw strings. |
| `DCTR-002` | Generic mismatch evidence cannot distinguish harness error from service-order error | Attribute the mismatch to one exact `TX-S01..TX-S11` group and retain both expected and observed closed token arrays. |
| `DCTR-003` | Recovery silently changes product authority semantics | Byte-bind `app/services/appointment_delete_physical.py`; allow edits only to harness, its focused test, the evidence schema and metadata. |
| `DCTR-004` | Repeated stateful attempts become an unbounded debugging loop | Permit one diagnostic attempt and at most one evidence-proven classifier repair attempt; any other or repeated failure stops. |
| `DCTR-005` | Failure path leaves a container, relay or network behind | Preserve exact-ID ownership reinspection, relay-first shutdown, captured-ID removal and absence proof on every outcome. |
| `DCTR-006` | A failed diagnostic is promoted to transaction acceptance | Retain failure evidence and require all twenty groups, final deterministic gates and one independent veto before a pass claim. |

No new data, command, route, database, provider, network or deployment authority
is granted by this delta.
