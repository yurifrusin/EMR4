# Threat-model delta: authored-synthetic shadow-comparison rehearsal

Date: 2026-08-12

Parent: `docs/security/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-threat-model-delta.md`

## New evidence surface

The tranche adds only a closed authored-synthetic fixture and a pure evaluator.
It adds no deployed component, trust boundary, identity, credential, endpoint,
database object, queue, sink, event consumer or command path.

## Threats exercised

| Threat | Fail-closed control |
|---|---|
| Missing or stale enablement is treated as consent | Six distinct denial scenarios require the full immutable-generation/global/practice/route/no-disable intersection. |
| Shadow code changes the authoritative result | The observer never receives the primary object; canonical bytes and digests must match before and after every scenario. |
| A mapped shadow candidate becomes executable | Only the parent pure adapter is called; its candidate remains inert, the kernel is never imported, and no command outcome exists. |
| Diagnostics disclose request, response or person data | Projections use only closed `syn-` labels and one-way digest fields; records have the exact 15-field allowlist and forbid bodies, identifiers, patient data and free text. |
| Observer overload or failure becomes request failure | Timeout, overflow and sink failure can only drop shadow evidence; observer failure is contained in one bounded record. |
| Diagnostic state feeds back into product behavior | All twelve response/command/client feedback edges remain forbidden and the evaluator has no route, response, transaction, audit or source capability. |
| Fixture tampering creates a false pass | Exact source hashes, a closed schema, recomputation of every scenario and hostile mutations fail closed. |

## Residual boundary

The rehearsal cannot establish real route placement, scheduling behavior,
latency, backpressure, queue isolation, sink availability, operational hashing,
retention or runtime dependency exclusion. Those remain closed for the later
separately reviewed default-off runtime-instrumentation plan.
