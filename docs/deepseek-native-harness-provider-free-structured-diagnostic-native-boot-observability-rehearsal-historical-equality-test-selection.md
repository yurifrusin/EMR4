# Structured diagnostic native-boot historical equality test selection

Date: 2026-08-21

Timestamp: 2026-08-21T09:58:44.5914356+10:00 (Australia/Brisbane)

Operation:
`deepseek-native-harness-provider-free-structured-diagnostic-native-boot-observability-rehearsal`

## Exact observation

The first widened compatibility selection included
`tests/test_deepseek_native_harness_pre_hmr_startup_terminal.py`. Two tests in
that file call the older recovery artifact builder and require its canonical
evidence to equal a fresh projection of the current authored-synthetic
controller:

- `test_recovery_contract_and_evidence_are_current_and_provider_disabled`;
  and
- `test_provider_disabled_validation_cannot_start_any_subprocess`.

That controller was intentionally changed by the later accepted attempt-003
terminal binding. The historical recovery evidence is immutable and must not
be regenerated to match the descendant controller. Both equality assertions
therefore return the already-known `evidence_not_current` relationship. They
started no Node, Harness, broker, worker, model or provider process and changed
no file.

## Frozen selection

The implementation and preexecution manifests exclude those two historical
current-projection equality nodes. The accepted v1 component remains directly
covered by this tranche's exact fallback-construction, canonical-byte and
exclusive-write tests, while the complete structured-seam, canonical wrapper,
materialization and new plan/controller suites remain selected.

This selection prevents a false requirement to rewrite immutable historical
evidence. It grants no acceptance waiver: any failure in the direct v1/v2
compatibility, package/source, process-count, terminal relationship, raw-value
retention or cleanup tests still fails closed before native execution.
