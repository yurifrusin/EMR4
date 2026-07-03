# plan-codex-codex-sprint-k1b-advisory-boundary-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-k1b-advisory-boundary-invariants` |
| Status | integrated |
| Created | 2026-07-04 05:27 +1000 |
| Source HEAD | `db65373` |

## Plan Summary

Adversarial invariant plan for K1b advisory retrieval non-authority in Bernie

## My Understanding

K1b should wire typed practice-knowledge retrieval into Bernie only as explanatory or suggestion support. The implementation must preserve a hard one-way boundary: retrieved facts can become provenance-bearing advisory frames/copy, but cannot set availability, slot candidates, roster truth, policy hard blocks, confirmation readiness, confirm/create payloads, freshness/session binding, audit/write evidence, or no-slot truth. This worker is plan-gated only, so no production or test code will be edited until explicit approval.

## Intended Surface / Boundary

Backend/domain invariant and route-level test surface around app/services/practice_knowledge, app/services/diary frames/policy/outcomes/confirm_gate, app/services/bernie evidence/session/outcome paths, and appointment proposal/confirm routes. Visually adjacent surfaces are Bernie panel cards/panels, booking slot rows, diary grid, waiting room/status affordances, and confirmation controls; they must not be redesigned by this invariant lane. If UI consumes advisory frames later, review/test_diary_smoke.py may get a narrow assertion that advisory text renders as support only while confirm affordance remains server-evidence-gated.

## Out Of Scope

Production code before approval; graph/vector store deployment; persisted PHI or session tables; auto-mode; broad API rewrite; master/handoff movement; runtime docs; taskpane or Command Centre; Diary grid redesign; using retrieved knowledge as a source of slot/search/roster/policy/session/audit/write truth; real PHI.

## Files I Expect To Edit

Expected implementation-phase edits: tests/test_practice_knowledge_advisory_boundary.py for strengthened envelope/import/boundary invariants; possibly tests/test_practice_knowledge_retrieval.py and tests/test_practice_knowledge_facts.py for outage/provenance/stale fixtures; Bernie route/outcome/confirm tests such as tests/test_bernie_booking_outcomes.py, tests/test_bernie_confirm_create_proposal.py, tests/test_bernie_signed_confirmation_evidence.py, tests/test_bernie_route_outcome_events.py, tests/test_bernie_session_routes.py, tests/test_diary_confirm_gate.py, tests/test_bernie_no_slot_suggestions.py, and tests/test_slot_search_normalized_execution.py for non-interference; only if K1b UI renders advisory frames, review/test_diary_smoke.py. Production files expected to inspect but not necessarily edit: app/services/practice_knowledge/*.py, app/services/diary/{frames.py,policy.py,outcomes.py,confirm_gate.py,schedule_explanations.py}, app/services/bernie/{evidence.py,session.py,outcomes.py,policy.py}, app/routers/appointments.py, app/routers/bernie_dev.py.

## Implementation Steps

1. Establish baseline by reading existing K1 advisory tests and Bernie confirmation/session/no-slot tests, then identify the exact planned K1b retrieval injection point. 2. Add malicious/stale/unavailable retriever fixtures that return facts claiming availability, roster overrides, policy exceptions, confirm permission, audit evidence, stale session freshness, or no-slot conclusions. 3. Assert the boundary adapter emits only BernieAdvisoryWarningFrame/status=advisory with preserved provenance and no fields consumed by policy, confirm_gate, slot search, signed evidence, session freshness, audit, or write payload builders. 4. Add route/outcome negative tests proving advisory frames may appear in explanations/suggestions but cannot change availability classification, candidate lists, outcome kind precedence, can_confirm/requires_confirmation, signed evidence validation, confirmed_warnings/audit_evidence, create proposal body, or appointment rows. 5. Add fail-closed tests for retriever outage, malformed/missing provenance, stale facts, and cross-session/cross-practice advisory metadata: Bernie should continue deterministic diary behavior or omit advisory support, never unlock confirm or rewrite no-slot truth. 6. If the UI consumes advisory frames, add a narrow smoke assertion that advisory support is visually separate from booking slot/confirm controls and does not alter existing Diary grid/status/waiting-room surfaces. 7. Run focused pytest subsets, py_compile for touched Python modules, node/review harness only if UI changes, and git diff --check.

## Visual / Behavioural Acceptance Checks

Plan acceptance means the later implementation will prove: retrieval cannot set availability, slot candidates, roster truth, policy hard blocks, confirmation readiness/can_confirm, confirm/create payloads, freshness/session binding, audit/write authority, or no-slot truth; retrieval outage or malformed/stale provenance fails closed to deterministic behavior; provenance is preserved for explanation only; stale or cross-session advisory content cannot satisfy signed evidence or session freshness; and any UI advisory rendering remains separated from booking slots, diary grid, waiting room/status panels, and confirm controls.

## Risks / Ambiguities

Main risk is an integration temptation to pass advisory frames through generic frame sets where policy/outcome precedence accidentally treats them as stronger evidence. Another risk is tests becoming too coupled to current route fixture names; prefer behavior assertions at the boundary and route outcomes. If K1b implementation needs production code to add the retrieval hook, this invariant lane should coordinate with the implementer so tests pin the hook as advisory-only rather than dictating a broad API rewrite.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: yes - integrated by Ariadne in Sprint K1b
