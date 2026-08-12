# Provider-free unmounted authored-synthetic shadow-comparison rehearsal design

Date: 2026-08-12

Status: `frozen_pure_rehearsal_design`

## Execution shape

This is a deterministic function over a closed JSON fixture. It constructs a
synthetic primary result and a separate digest-only projection, snapshots the
primary bytes, evaluates the shadow scenario, then snapshots the primary again.
The shadow evaluator never receives a reference to the primary result.

The 24-field projection is converted to the parent adapter's raw-envelope shape
using only one-way digest labels and presence bits. This exercises the accepted
pure adapter without importing `app`, starting FastAPI, opening PostgreSQL or
invoking any route or kernel function.

## Admission and ordering

Admission uses the accepted expression unchanged:

`current generation AND global enabled AND practice enabled AND exact route
allowlisted AND NOT externally disabled`.

All missing, unknown, disabled, stale or externally disabled states return
`disabled_no_observation`. Fault injection is considered only after admission.
Overflow and timeout stop before adapter comparison. Sink failure occurs only
after a single minimized record candidate has been built.

## Comparison rules

- a current raw projection must reject with the sorted three-code gap set;
- a partial projection that supplies only the backend precondition is an
  `unexpected_gap_set`;
- a complete raw projection where current gaps were expected is an
  `unexpected_candidate_mapped`;
- a complete candidate matching the independently frozen semantic digest is
  `candidate_projection_equivalent`; and
- a complete candidate whose only difference is `command_digest` is
  `candidate_projection_divergent` with exactly that mismatch code.

Semantic comparison excludes only `route_adapter_id`, preserving the parent
adapter's provenance rule. Candidate values remain inert `syn-` digests and the
candidate always retains `runtime_execution_authorized: false`.

## Diagnostic record

An emitted record has exactly the accepted 15 fields. It contains route and
operation labels, one-way scope/correlation/request digests, sorted gap or
mismatch codes, comparison/timing/overflow classes and a fixed synthetic
timestamp. It contains no projection, candidate, request or response body,
direct identifier, patient data, free text, token, credential, source state,
authority decision, command outcome, mutation receipt or audit receipt.

Records exist only inside the committed authored-synthetic evidence fixture.
No operational sink, persistence, retention or aggregation design is selected.

## Failure asymmetry

The observer-failure scenario emits one safe bounded failure record. Timeout and
overflow emit none. Sink failure discards its one in-memory record candidate.
All failures are terminal for the shadow attempt, require no retry and leave the
canonical primary bytes unchanged. This proves diagnostic loss is tolerable; it
does not prove operational reliability.
