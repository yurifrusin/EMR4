# Governance clockwork typed serial-continuation state projection rehearsal — plan

Date: 2026-08-23

Timestamp: 2026-08-23T19:41:32.8076827+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`ariadne-provider-free-governance-clockwork-typed-serial-continuation-state-projection-rehearsal`

## Purpose

Replace repeated hand-authored serial continuation runtime-state objects with
one compact typed intent inside the existing orchestrator preflight. Preserve
the existing receipt, five-source, latch, parallelism, settings-fingerprint,
Git-object, Git-ref, untracked-path and fail-closed validation.

This is the second ranked ergonomic repair from the accepted matched efficacy
review. It is a replacement interface, not a new approval layer, receipt,
ledger, writer or control plane.

## Exact source and baseline

The starting task HEAD is
`c00cb29095fce3c0c08f83ec26efbbf7926bb488`.

The fresh manual preplanning state for this tranche contains 114 caller scalar
leaves, 202 lines and 9,345 bytes. Its generated receipt contains 125 lines and
6,846 bytes. The pair therefore contains 327 lines and 16,191 bytes before the
projection rehearsal.

These are tranche measurements, not permanent test constants. Tests must
derive comparisons from their supplied intent and materialized state.

## Owned implementation files

Implementation ownership is limited to:

- `orchestration_harness/orchestrator_preflight.py`;
- `scripts/ariadne_orchestrator_preflight.py`; and
- `tests/test_ariadne_orchestrator_preflight.py`.

The existing requirements, adapter, worker-pool and active-latch files are
read-only inputs. Their settings fingerprint must not change.

## Compact intent contract

Add the recursively closed schema
`ariadne.serial_continuation_intent.v1` with exactly:

- `schema_version`;
- `preset`;
- `continuation_event`;
- `planned_action`;
- `assessed_stage`;
- `active_evidence_paths`; and
- `lane_decision_overrides`.

The only admitted preset is
`provider_free_serial_observed_empty_workers`. Selecting it is the operator's
typed assertion that this continuation has no assigned worker, workspace
receipt or active/stale managed worker instance. It is not a process probe.

`continuation_event` must use the configured closed event vocabulary and must
not be `pre_worker_dispatch`. `planned_action` and `assessed_stage` remain
bounded non-empty text because their content is tranche-specific rather than a
finite state.

`active_evidence_paths` must contain 1..32 unique, existing, repository-relative
files under the admitted documentation and orchestration evidence roots. Path
escape, absolute paths, backslashes, directories and missing files reject.

`lane_decision_overrides` is a unique list of objects containing only
`lane_id` and `decision_code`. Lane IDs remain exactly `deepseek_flash`,
`gemini_verifier` and `native_subagents`. Decision codes are closed to:

- `declined_negative`;
- `declined_neutral`;
- `not_applicable_neutral`; and
- `reserved_required_independence`.

The preset supplies the three default decisions. An override selects a fixed
disposition, leverage and lane-distinct rationale; it cannot add free-form
rationale or a work package. `planned`, `dispatched` and `completed` remain
impossible through the serial interface.

## Derived runtime state

The existing CLI gains `--continuation-intent` as a mutually exclusive peer of
`--runtime-state`. It materializes an in-memory
`ariadne.orchestrator_runtime_state.v1` and passes it through the unchanged
receipt validator. It does not write a full runtime-state file.

The projection derives:

1. the complete current active latch from the requirements-owned canonical
   latch path;
2. all five source-evidence entries from fixed repository paths plus the
   supplied active evidence paths;
3. the orchestrator context-health record and exact five-source list;
4. every declared adapter observation, with the primary Codex session
   `reachable` and every unprobed external adapter `unknown`;
5. every managed worker-slot object with empty active/stale lists under the
   observed-empty preset;
6. empty assigned-agent and workspace-receipt lists;
7. the three-lane assessment, zero parallel packages, fixed serial constraints
   and fixed reassessment triggers; and
8. no Git object IDs in caller prose, leaving Git binding to the existing
   machine snapshot and latch source resolution.

The existing `--runtime-state` path remains unchanged for occupied worker,
workspace, dispatch or other non-serial continuations.

## Verification and measurement

Deterministic verification must prove:

1. a compact current-tranche intent produces a passing existing receipt;
2. its receipt preserves the exact active-operation projection, five source
   names, settings fingerprint, Git-object resolution, Git-ref snapshot,
   protected-ref alignment, untracked branding preservation, terminal guard
   and dispatch decision of an equivalent manual serial state;
3. the intent contains at most 25 scalar leaves and 40 lines;
4. caller scalar leaves fall by at least 75 percent and total intent-plus-receipt
   lines and bytes fall by at least 40 percent against the measured manual pair;
5. no expanded runtime-state artifact is written;
6. extra keys, invalid presets/events/decision codes, duplicate lanes, hostile
   paths, missing evidence and non-empty-worker implications reject before a
   receipt is accepted;
7. a changed or invalid canonical latch, settings fingerprint, adapter method
   or managed worker inventory still fails closed;
8. `pre_worker_dispatch` is unavailable through this serial preset;
9. the legacy runtime-state CLI and its existing tests remain unchanged; and
10. Ruff and the provider-free orchestrator/governance suites pass.

Use the compact intent for the tranche's later serial continuation receipts so
the rehearsal proves occupied ergonomics rather than fixture-only behavior.

## Parallelism assessment

- **DeepSeek:** declined. The native occupied profile remains paused, Claude
  Code is not a fallback, and this tranche changes tightly coupled preflight
  safety semantics.
- **Gemini:** declined. Schema closure, exact projection and receipt equivalence
  are deterministic; no provider veto is authorised.
- **Native subagents:** declined under developer policy and because the compact
  intent, materializer, CLI and validator tests form one serial contract.
- **Owner:** GPT Sol.

Reassess only if the implementation requires settings-policy changes, cannot
preserve receipt equivalence, or reveals a genuinely separable non-authority
test package after the contract is committed.

## Acceptance

The rehearsal passes only if one compact typed intent replaces the manual
runtime state for a real serial continuation, meets both efficacy thresholds,
and leaves every existing receipt safety decision intact. A reduction obtained
by omitting a required source, lane, latch, adapter, worker-slot, Git or terminal
guard fails.

## Next tranche

After acceptance, use the new projection for ordinary serial closeouts and
measure several live tranches before deciding whether postpublication canonical
validation can safely replace any full governance-suite repetition. Do not
pre-authorise test-cadence reduction in this rehearsal.

## Claim boundary

Passing proves only a smaller provider-free serial preflight input with matched
receipt safety. It does not qualify occupied workers, the native DeepSeek
Harness, Claude fallback, provider/model reliability, live slot discovery,
product behavior, patient or clinical data, runtime, deployment, release,
Pages, protected evidence or protected refs.
