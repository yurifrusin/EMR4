# H64 Bernie Interpretation Harness Independent Review

## Review Context

Reviewer: Shen, DeepSeek Flash worker.

Mode: read-only adversarial review. No files were edited by the worker, no raw
diary/trove material was accessed, and no provider calls were made.

Scope: the H63 independent-review brief and the provider-free Bernie
Interpretation Harness readiness/gate stack.

## Verdict

No critical or high findings were reported. The stack remains suitable as a
blocked-by-default preflight for continued provider-free harness work.

The review found three medium hardening items that should be addressed before
any later sprint proposes runtime route wiring, provider prompts or dry-runs,
memory/RAG/GraphRAG wiring, H15/H-series runtime imports, or historical diary
material access.

## Findings

| ID | Severity | Finding | Ariadne triage |
|---|---|---|---|
| H64-M1 | Medium | Readiness `runtime_or_provider_wiring_ready` and `raw_trove_access_ready` values are currently explicit blocked constants rather than derived from the runtime-gate scope. | Accept. H65 should derive readiness booleans from gate scope and add negative tests. |
| H64-M2 | Medium | Protocols require the readiness command before runtime/provider/trove proposals, but the requirement is process-enforced rather than mechanically enforced against touched runtime/provider surfaces. | Accept as release-gate debt. Add a pre-runtime checklist or static guard before any runtime/provider proposal. |
| H64-M3 | Medium | Public interpretation result/frame helpers rely on tests to call invariant assertions; the helpers do not self-validate returned objects. | Accept. A bounded harness-only sprint should add self-validation without changing runtime authority. |
| H64-L1 | Low | Report safety currently checks a small static subset of utterance fragments rather than all committed fixture utterances. | Accept. Make report safety derive forbidden utterance text from fixtures. |
| H64-L2 | Low | Reviewer flagged Unicode confusability risk. | Already covered for current scope: `_normalize_utterance()` uses NFKC normalization and strips format controls. |
| H64-L3 | Low | Blocked-readiness snapshot has no independent checksum/integrity guard. | Defer. Snapshot integrity is useful, but H64-M1 gives stronger derivative protection first. |
| H64-L4 | Low | Clarification frame invariant uses either patient-context or reason-code shape instead of enforcing exactly one clarify subtype. | Accept. Fold into the self-validation hardening sequence. |

## Confirmed Strengths

- Current artifacts are explicit that runtime/provider wiring, historical diary material access, and raw-trove access remain blocked.
- Production `app/` runtime isolation tests guard against imports or references
  to interpretation harness tooling, fixture paths, H15/H-series materials,
  `local_data`, and trove paths.
- Projected-frame contracts already block confirmation bypass, invented
  availability, route escalation, and payload leakage in the tested surface.
- Runtime gate pause triggers cover decision, scope, required-review, and
  forbidden-use changes.

## Recommended Sprint Sequence

1. H65: derive combined readiness booleans from runtime-gate scope and test
   mismatch/fail-closed behavior.
2. H66: make interpretation result/frame projection self-validating and tighten
   clarification frame subtype invariants.
3. H67: derive forbidden report text from fixture utterances instead of a fixed
   subset.
4. H68 or pre-runtime gate: add a mechanical readiness-reference guard for any
   runtime/provider/trove proposal surface.

Sprint engine state: continuing. No user intervention is required because the
review found no critical/high issue and did not recommend unblocking runtime,
provider, memory, or trove access.
