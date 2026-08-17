# Threat-model delta — Arrival/check-in command-family convergence review

Date: 2026-08-18

Timestamp: 2026-08-18T06:20:30.8340302+10:00 (Australia/Brisbane)

Status: `frozen_for_read_only_execution`

Task baseline: `fb39d235c5dc4de2440a5b0e4685ee5da5b4f4d0`

## Assets protected

- one authoritative product-facing meaning for ordinary appointment check-in;
- the distinction between an appointment state and the business command that
  creates it;
- current human authority, locked source truth, one-use evidence,
  idempotency, waiting-area compatibility, attributable audit, committed event,
  strict receipt and fresh readback;
- the default-off authored-synthetic A5.1 admission boundary; and
- protected refs, sealed evidence and unrelated untracked files.

## Threats and fail-closed controls

| Threat | Fail-closed control |
|---|---|
| Treating `status=Arrived` as proof that check-in semantics were satisfied | Compare role, transition, waiting-area, evidence, event and receipt contracts; select the domain command, not merely the resulting value. |
| Allowing two canonical product paths for ordinary check-in | Freeze one future atomic cutover: first-party clients move to dedicated check-in while general status ceases to admit ordinary `Arrived` intent. |
| Mistaking the default-off A5.1 gate for reusable product policy | Separate Rayleen naming, feature flag and authored-synthetic allowlist from the deterministic check-in kernel in the successor. |
| Broadening the initial role policy by analogy | Preserve exact Receptionist-only A5.1 evidence; any later role expansion requires a separately justified policy decision. |
| Losing waiting-area integrity during consolidation | Preserve active, same-practice, same-location assignment/preservation checks and the no-move/no-removal A5.1 boundary. |
| Losing one-use confirmation semantics by reusing generic status evidence | Preserve A5.1 evidence-hash consumption in the canonical check-in contract. |
| Treating an event as authority or current truth | The event records a committed result and remains an acceleration hint; command-time database truth and fresh readback remain authoritative. |
| Updating stale grammar before product admission is real | Classify static statements in this review; defer edits until the reusable adapter and route cutover are admitted. |
| Hiding baseline route-contract defects | Record typed-path normalization and literal-shadow false-positive behavior as bounded negative evidence. |
| Widening the review into runtime work | Product, API, schema, service, migration, client and product tests remain read-only. |

## Residual risk and claim boundary

The selected architecture does not itself make A5.1 a generally admitted
product command. Until the later atomic cutover, first-party clients continue
to use generic status for `Arrived`, A5.1 remains default-off, and the static
grammar remains scope-qualified rather than corrected.

Passing proves only a repository-static semantic decision and the boundary of
one successor extraction rehearsal. It does not prove live database behavior,
general-practice admission, client usability, deployment or production safety.
