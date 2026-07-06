# plan-claude-claude-sprint109-band2-provider-gate-criteria

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/sprint109-band2-provider-gate-criteria` |
| Source Task | `claude-sprint109-band2-provider-gate-criteria` |
| Status | integrated |
| Created | 2026-07-07 00:19 +1000 |
| Source HEAD | `f5e16705` |

## Plan Summary

Sprint 109 Band-2 provider gate criteria plan

## My Understanding

Plan-only: define exact criteria, evidence commands, approval payload shape, and blocked values that must remain blocked before any Bernie/Access AI runtime-provider or live-smoke gate could be approved. No production code, no provider enablement.

## Intended Surface / Boundary

Docs/orchestration proposal artifact only: a new docs/ proposal file plus references to orchestration/bernie_release_gates.md, docs/bernie-interpretation-harness-runtime-gate.json, scripts/bernie_interpretation_readiness_check.py. No app/ code, no gate JSON value changes.

## Out Of Scope

No code wiring; no provider/live/fake-provider enablement; no GCP/ADC; no route/schema/model mutations; no GraphQL mutations; no H15/trove runtime imports; no memory/RAG/GraphRAG; no model-to-DB writes; no changing any decision from blocked or any scope value to true.

## Files I Expect To Edit

docs/bernie-band2-provider-gate-criteria.md (new proposal doc, plan phase only). No edits to app/, gate JSON, or scripts.

## Implementation Steps

1) Enumerate Band-2 gate criteria (bounded no-write runtime plan, provider privacy/cost review, route-authority review, staff-confirmation affordance, audit/observability, rollback/kill-switch, focused tests + manual review). 2) List required evidence commands (readiness_check, runtime_gate_check, proposal_surface_guard, Margaret/Dr Shera happy-path gate, live_provider:true labeling rule). 3) Define approval payload shape modeled on h15-approved-gate.json (reviewer=yuri, decision, scope booleans, expiry). 4) State blocked values that MUST remain blocked (runtime_gate_decision=blocked, runtime_or_provider_wiring_ready=false, raw_trove_access_ready=false, all scope=false). 5) Mark exact points where Yuri approval is mandatory before any gate change.

## Visual / Behavioural Acceptance Checks

Artifact is proposal-only; names blocked gates that remain blocked; states explicit Yuri-approval requirement before any gate change; cites exact evidence commands and the current blocked expected values. No app/UI surface changes; diary grid, waiting room, booking slots, cards, panels, status all unchanged.

## Risks / Ambiguities

Risk: proposal doc discussing runtime/provider surfaces must itself pass bernie_interpretation_proposal_surface_guard.py (include readiness command + expected blocked values). Risk: must not be read as approval. Ambiguity: 'Band-2' checkpoint level - treated as the runtime-provider/live-smoke movement gate per AGENTS.md Sprint 109 note.

## Codex Plan Review

- Review result: accepted and synthesized into
  `docs/bernie-band2-provider-gate-criteria.md`.
- Required changes before implementation: keep as proposal-only; do not change
  gate JSON or app/runtime code.
- Approved to proceed: no separate Claude implementation required.
