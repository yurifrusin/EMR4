# Threat-model delta — provider-free read-only check-in attempt-008 plan admissibility

Date: 2026-08-23

Timestamp: 2026-08-23T06:12:47.9140198+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-decision`

This delta covers only deterministic comparison of accepted unprotected
evidence. It opens no attempt plan, database, product, provider or runtime.

## Assets

- the exact fourteen-row prerequisite population;
- the distinction between plan admissibility and execution readiness;
- immutable attempt-007 negative evidence and accepted repair lineage;
- machine-resolved full Git ancestry and canonical source digests; and
- the continued absence of attempt-008 occupied artifacts.

## Threats and controls

| ID | Threat | Fail-closed control |
|---|---|---|
| `AD-001` | A positive verdict is interpreted as execution authority. | The only positive value is `admissible_for_separate_plan_freeze`; P06-P14 remain non-satisfied obligations and every occupied surface stays closed. |
| `AD-002` | The assessor silently omits a historical prerequisite. | Contract and schema require exactly P01-P14 with exact descriptions, stages and expected states. |
| `AD-003` | A plan obligation is relabelled satisfied. | Exact per-row state mapping rejects promotion of P06-P14. |
| `AD-004` | Unaccepted or drifted evidence satisfies a row. | Exact source/result/schema/digest and Git-ancestry bindings reject before decision output. |
| `AD-005` | Attempt 007 is reclassified or retried. | Immutable terminal bytes, occupied count one, retry zero and failed-closed result are mandatory. |
| `AD-006` | The repair claim exceeds its deterministic evidence. | P03-P05 use exact accepted counts and closed activity fields; database semantics remain unproved. |
| `AD-007` | An attempt-008 plan or namespace already exists. | Exact target paths must be absent; presence makes the verdict `not_admissible`. |
| `AD-008` | An abbreviated Git display is expanded manually. | Git sources are read mechanically; caller-authored derived objects are forbidden. |
| `AD-009` | Repository tests load database conftest. | Closed-authority v2 manifests admit only `scripts.ariadne_provider_free_pytest`. |
| `AD-010` | The read-only assessor launches Docker, a database, network or provider. | Implementation admits no such imports or subprocess coordinates; focused tests enforce zero forbidden activity. |
| `AD-011` | Free-form decision/status vocabulary drifts. | Contract and schema own exact verdict and row-state enumerations. |
| `AD-012` | Protected or user-owned paths move. | Protected-ref readback, explicit-path staging and preserved `docs/branding/` checks remain mandatory. |

## Residual risk

A plan-admissibility verdict cannot predict the next occupied database result.
It says only that the known deterministic blockers have accepted controls and
that the remaining work can be frozen as explicit plan/preexecution
obligations. An attempt-008 plan may still fail deterministic admission and an
admitted occupied attempt may still fail closed.
