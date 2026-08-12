# Threat-model delta: compatibility conformance-harness readiness repair

Date: 2026-08-12

Parent: `docs/security/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review-threat-model-delta.md`

Status: `frozen_test_only_delta`

| Threat | Fail-closed control |
|---|---|
| Making stale tests green by weakening product controls | Application files are outside ownership; temporal and proposal-idempotency admission remain unchanged. |
| Hiding a same-day elapsed-time race | Same-day suites freeze the clinic clock before their exercised appointment times and retain the actual test date. |
| Reintroducing calendar decay | Weekday-specific suites derive the next required weekday and all date assertions use the same fixture value. |
| Treating an absent proposal identity as valid | Successful proposal fixtures send deterministic non-empty `Idempotency-Key` values; required-header behavior is not bypassed. |
| Changing validation precedence unintentionally | Deliberately invalid proposal bodies and their expected `422` outcomes remain unchanged. |
| Broadening the repair into runtime work | Only eight named test files plus tranche evidence are owned; no application, route, database, provider, command or deployment surface opens. |
| Losing user-owned material during closeout | `docs/branding/` and all unrelated untracked files remain excluded; staging is explicit-path only. |

This repair generates no product, patient, clinical, provider or operational
evidence. A passing suite proves only that the existing compatibility contract
is exercised by current deterministic fixtures.
