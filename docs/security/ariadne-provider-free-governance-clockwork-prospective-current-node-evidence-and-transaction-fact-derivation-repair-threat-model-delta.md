# Governance clockwork prospective evidence and transaction-fact repair — threat-model delta

Date: 2026-08-23

Timestamp: 2026-08-23T16:18:40.5972422+10:00 (Australia/Brisbane)

Status: `frozen`

## Scope

This delta covers one provider-free change to the existing governance
clockwork preparation and CLI output. It adds no product, Harness, provider,
network, database, credential, actuator or protected-ref surface.

## Threats and controls

| Threat | Control |
|---|---|
| A prospective node publishes before all human evidence is valid | Validate all `plans`, `closeouts` and `acceptances` paths before transaction projection and before canonical writes. |
| Validation stops at the first error and causes repeated correction cycles | Collect a deterministic ordered error set across every prospective human-evidence path in one preparation pass. |
| The new validator drifts from the repository's timestamp rule | Make the consistency test consume the production validator; retain hostile rule-specific fixtures. |
| Path validation reads outside the repository or touches branding | Admit only safe relative Markdown paths, reject traversal/absolute/backslash paths and reject `docs/branding/`. |
| Operator-supplied counters become false authority | Accept no new intent field; derive command-local attempt, lease, generation, publication, readback and rollback facts from prepared or committed state. |
| Cumulative history is inferred from an incomplete current reading | Label facts as command-local; do not claim historical totals without retained machine outputs. |
| A broad refactor weakens rollback safety | Keep the canonical writer, pointer-last commit, lease, predecessor digest and byte-exact rollback implementation unchanged. |
| The repaired path is used before its fixtures pass | No live clockwork publication may use the repaired implementation until the focused and full governance suites pass. |
| A new helper becomes another bureaucratic layer | Implement inside the existing tick and CLI files; add zero operator fields, approvals, gates, schemas, ledgers or required documents. |
| Protected or product scope expands during workflow repair | The active latch prohibits provider, product, data, runtime, deployment, Pages, protected-evidence and protected-ref effects. |

## Claim boundary

Passing evidence will show only that the existing tick rejects the complete
prospective human-evidence error set before publication and emits exact
command-local transaction facts. It will not prove all future closeouts are
error-free, native-Harness reliability, provider suitability, product
correctness, production readiness or protected integration safety.
