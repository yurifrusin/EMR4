# Provider-free unmounted default-off shadow-comparison architecture

Date: 2026-08-12

Status: `frozen_unmounted_architecture`

## Placement and ownership

The primary appointment handler owns authentication, authorization, domain
logic, transaction disposition, audit and the HTTP result. The shadow boundary
is downstream of a sealed primary result. Its handoff is one-way and
best-effort: it cannot return a value or exception to the handler.

The hook is conceptual only. A later implementation would need to prove that
its module dependencies exclude response writers, database sessions, command
services, source adapters, event publishers and audit writers. This tranche
does not choose a queue, thread, process or storage service.

## Admission

A signed or operator-controlled runtime switch is not designed here. The
architecture specifies only the deterministic decision:

`current_generation AND global_enabled AND practice_enabled AND route_allowed
AND NOT externally_disabled`.

Every missing or unknown value is denial. Generations are immutable; any
amendment creates a new generation. The external switch is monotonic within a
generation: it may disable immediately and cannot enable.

## Projection

The handler-side boundary creates a `ShadowRouteProjection`, not a request
copy. Direct identifiers are replaced by versioned one-way digests and fields
unrelated to conditional-command structure are omitted. Presence flags make
missing precondition, confirmation and idempotency evidence observable without
inventing their values.

The observer may construct only a `ShadowConditionalAppointmentCandidate`.
The type is deliberately not the executable kernel request, carries
`runtime_execution_authorized: false`, and cannot cross into the command
service. This preserves useful mapping comparison without creating a second
write path.

## Comparison and record

For the present raw shapes, the expected comparison is the exact three-gap set
proved by the parent rehearsal. A future complete projection could instead be
compared against an independently supplied expected semantic digest. The
closed comparison classes are:

- `expected_current_gap_match`;
- `unexpected_gap_set`;
- `unexpected_candidate_mapped`;
- `candidate_projection_divergent`;
- `candidate_projection_equivalent`;
- `observer_failed`; and
- `disabled_no_observation`.

The diagnostic record contains only generation/config digests, adapter and
operation labels, one-way scope/correlation/request digests, adapter result,
sorted gap or mismatch codes, comparison class and timing/overflow categories.
It is not an audit record, command receipt, authority decision or product
truth. Persistence, retention and operational aggregation are explicitly
unselected.

## Failure semantics

Observer admission failure, projection failure, comparison failure, timeout,
capacity overflow and sink failure all converge on no record or a bounded
observer-failure record where safe. The primary result is immutable before any
of them occurs. No retry is required and loss is acceptable.

This asymmetry is intentional: command correctness cannot depend on a
diagnostic path, while diagnostic evidence may be incomplete.
