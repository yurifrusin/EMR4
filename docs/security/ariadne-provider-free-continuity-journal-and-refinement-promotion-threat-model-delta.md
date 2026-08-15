# Threat-model delta — Ariadne continuity journal and refinement promotion

Date: 2026-08-15

Timestamp: 2026-08-15T17:27:59+10:00 (Australia/Brisbane)

Source HEAD: `ac638c45a3a1916162424cd42518764af39df7f7`

Status: `frozen_for_provider_free_harness_implementation`

## Scope

This delta covers pure development-harness validation and decision logic only.
It creates no persistent daemon, command runner, model runtime, executable
skill or Raisa product surface.

## Threats and controls

| Threat | Frozen control |
|---|---|
| A duplicate command causes a second effect | Exact completed repeats return only the recorded digest; unfinished or uncertain commands never auto-replay. |
| One command id is reused for different work | Stable id plus exact request digest; any mismatch is a terminal conflict. |
| A worker restart makes a received command look absent | Recovery marks unfinished prior-generation state explicitly uncertain. |
| Old events contaminate a new worker generation | Cursors are `(generation, sequence)`; retired/future/out-of-range cursors require an authoritative snapshot. |
| Missing events are hidden | Sequence must be contiguous inside each generation. |
| A failed test is rerun without any changed evidence | Exact unchanged failure returns `diagnose_without_rerun`. |
| A transient transport or provider failure is cached as a substantive failure | Only the closed `deterministic_failure` result is memoizable; transient outcomes are `uncertain` and require resolution. |
| A materially changed input is omitted from a gate fingerprint | The composite requires source HEAD/tree, evidence set, manifest, relevant inputs and toolchain; missing components fail closed. |
| A stale pass is applied to changed code | Pass reuse requires exact candidate/evidence and manifest fingerprints. |
| Uncertainty is treated as failure or success | It has its own closed decision `resolve_uncertainty`. |
| A model edits Ariadne policy directly | Refinement emits a quarantined typed proposal only; no apply mechanism exists. |
| A proposal smuggles executable capability | Closed non-executable kinds and bounded text/digest fields make code, commands, dependencies and credentials unrepresentable. |
| A proposer certifies itself | Promotion authority must be distinct; global promotion additionally requires a distinct independent reviewer. |
| Review covers a different candidate | Proposal, deterministic evidence, source HEAD, review and promotion bind exact digests. |
| A local lesson silently becomes global | Scope is exact and immutable; global promotion has stricter evidence. |
| Rollback guesses prior content | Rollback names an exact promoted decision and recorded base digest; it applies nothing itself. |
| History is rewritten | Generations and decisions are append-only inputs to pure validation; in-place mutation is rejected. |
| Journal evidence is mistaken for command authority | Policy and outputs state that the journal executes nothing and grants nothing. |
| Harness controls leak into Raisa | Source scope excludes application, migration, API, database and Diary code. |

## Residual risk

- Filesystem crash durability, atomic append, concurrent writers and supervisor
  recovery are not implemented or proved.
- A deterministic digest proves byte identity, not the truth or adequacy of the
  evidence it binds.
- Human or model-authored refinement text may still be poor; promotion controls
  provenance and separation, not semantic perfection.
- No automatic application path exists, so a promoted decision still requires a
  separately reviewed ordinary repository change.

## Authority boundary

No command execution, model/provider call, network, database, product data,
patient/clinical data, executable skill, automatic self-modification,
deployment, production, release, Pages or protected-ref authority is granted.
