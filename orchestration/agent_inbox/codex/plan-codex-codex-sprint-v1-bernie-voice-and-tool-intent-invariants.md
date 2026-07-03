# plan-codex-codex-sprint-v1-bernie-voice-and-tool-intent-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-v1-bernie-voice-and-tool-intent-invariants` |
| Status | integrated |
| Created | 2026-07-04 05:50 +1000 |
| Source HEAD | `98d3143` |

## Plan Summary

Adversarial invariant plan for Bernie voice and typed tool-intent routing

## My Understanding

Sprint V1 is about proving the reception voice/tool-intent boundary before implementation. Bernie may phrase helpful reception answers, cite typed practice-knowledge advisory frames, and propose diary actions such as extending an appointment, but model wording, retrieved facts, and user-suggested commands must never directly mutate appointments, mint confirmation authority, fabricate edit evidence, bypass proposal/confirm gates, or blur whether an assertion came from deterministic diary state, staff input, model wording, or practice-knowledge retrieval.

## Intended Surface / Boundary

Primary surface is backend Bernie/Diary interpretation and command/proposal/confirm contracts around typed tool intents, especially non-booking requests such as appointment extension/update. Adjacent visible surface is the Diary Bernie panel only if it consumes typed intent state; any UI checks should prove displayed cards, slots, panels, waiting-room/status labels, and diary-grid affordances remain non-authoritative unless backed by deterministic server state. Nearby surfaces that must not change: clinical scribe/consultation flows, taskpane Command Centre, broad diary grid layout, patient-flow/waiting-room mutation controls, persisted session storage, and auto-mode writes.

## Out Of Scope

No production code during this plan gate. For implementation, no broad API rewrite, no persisted PHI/session tables, no direct auto-mode diary writes, no clinical scribe/consultant retrieval, no changes to visual diary layout unless a tiny test hook is explicitly needed for typed intent rendering, and no expansion of retrieval into slot, roster, policy, confirm, freshness, audit, or write-payload authority.

## Files I Expect To Edit

Expected implementation edit candidates after approval: focused tests under tests/ for Bernie interpretation/session/proposal/confirm/advisory boundaries; possibly review/test_diary_smoke.py or review fixtures if the Diary panel renders typed intents; narrowly scoped Bernie/appointment service or router files only if tests expose missing typed-intent guardrails, likely app/routers/appointments.py and app/services/diary/* or app/services/practice_knowledge/* seams already used by K1/K1b. No app/docs runtime assets unless approved by failing tests and needed for typed-intent display.

## Implementation Steps

1. Map the current Bernie intent/proposal/confirm path for booking and appointment update/extend requests, identifying which component owns truth for diary state, candidate/proposal evidence, confirmation affordance, and write payload. 2. Add adversarial tests that inject model text, retrieved advisory facts, and staff/user-suggested action wording that claim an appointment can be extended or edited, and assert these inputs can only produce proposal/explanation states, never direct writes or confirm-grade evidence. 3. Add stale/tampered/mismatched proposal tests so extension/update confirms fail unless tied to current deterministic appointment state and signed/server-owned evidence where applicable. 4. Add authorship/source separation tests proving UI/state payloads distinguish deterministic diary facts, staff selections, model explanations, and practice-knowledge advisory frames. 5. If typed intents are rendered in the Diary Bernie panel, extend the deterministic review harness with narrow selector assertions that practice-reference cards or intent summaries do not create booking-slot rows, status controls, confirm buttons, or waiting-room mutations. 6. Run focused pytest suites, py_compile for touched Python, node checks for touched JS, the Diary review harness if UI touched, and git diff --check.

## Visual / Behavioural Acceptance Checks

Adversarial cases prove no direct appointment writes from model/retrieval/user text; no confirm bypass from wording; stale proposal rejection for appointment edit/extend; no fabricated appointment-edit evidence; clear authorship/source labels in state payloads; advisory practice-knowledge remains advisory-only; any visible Diary cards/panels/slots/status affordances are display-only unless backed by server proposal/confirm state; no regressions in existing Bernie booking/proposal/confirm and K1b advisory-boundary tests.

## Risks / Ambiguities

The current code may not yet have a separate typed intent model for non-booking requests, so some tests may initially need a small normalizer/adapter seam rather than only assertions. Appointment extension semantics must be defined carefully: extension should probably become an update proposal over duration/end time, not a privileged command. If UI rendering is not present yet, avoid inventing visual work and keep UI review to future-facing harness requirements. Biggest ambiguity is where confirm evidence for edit/extend should bind: appointment id, original state/version, proposed duration/time, staff actor, and freshness window should be named before implementation.

## Codex Plan Review

- Review result: Accepted and implemented by Ariadne as a narrow backend/frame V1 slice while Claude was session-capped.
- Required changes before implementation: Keep the route non-mutating, require visible diary context, and delegate to existing appointment-update proposal authority.
- Approved to proceed: implemented by Ariadne
