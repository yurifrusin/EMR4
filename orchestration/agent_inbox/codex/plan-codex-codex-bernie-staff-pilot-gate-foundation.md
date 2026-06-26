# plan-codex-codex-bernie-staff-pilot-gate-foundation

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-staff-pilot-gate-foundation` |
| Source Task | `codex-bernie-staff-pilot-gate-foundation` |
| Status | integrated |
| Created | 2026-06-27 08:46 +1000 |
| Source HEAD | `fc4e6c3` |

## Plan Summary

Backend default-off Bernie staff pilot gate

## My Understanding

Create only the backend/config foundation for a staff-visible Bernie review pilot. The sprint should not expose a frontend panel or broaden existing dev/query review behaviour; it should add a deterministic, centrally testable eligibility signal that later diary/frontend code can call before rendering Bernie review outside explicit dev mode.

## Intended Surface / Boundary

Backend API/config only. Intended surface is a new authenticated, non-mutating Bernie pilot eligibility helper and route under the appointments API, plus settings that default to disabled. Visually adjacent surfaces that must not change: diary grid, appointment cards, booking slots, waiting room, status controls, Bernie review panel, dev-review query parameters, taskpane, and Command Centre.

## Out Of Scope

No frontend UI exposure; no diary/taskpane/Command Centre edits; no production/default enablement; no autonomous Bernie writes; no appointment mutation semantics; no DB migration unless implementation review proves config alone is insufficient; no PHI or real account allowlists; no Google/Gemini/provider calls; no broad refactor of appointment or Bernie route logic.

## Files I Expect To Edit

Expected production files: app/config.py for default-off non-PHI settings; app/services/bernie_pilot_gate.py for UUID allowlist parsing and eligibility decision; app/schemas/appointments.py or a small dedicated schema module for the eligibility response; app/routers/appointments.py for a narrow GET /api/v1/appointments/bernie/pilot-eligibility route. Expected tests: tests/test_bernie_staff_pilot_gate.py. Orchestration-only plan/review packet files may be edited during this plan gate.

## Implementation Steps

1. Add default-off settings for Bernie staff pilot enablement and practice/user UUID allowlists, represented as non-PHI config strings. 2. Implement a pure helper that receives settings plus the authenticated User and returns deterministic eligibility details without DB writes. 3. Add a small response schema with fields such as enabled, eligible, reason, practice_allowed, user_allowed, and surface='bernie_staff_review'. 4. Add an authenticated GET eligibility route using existing staff appointment roles; the route should not call supervised booking, confirmation, slot search, LLM, audit, or provider paths. 5. Add focused pytest coverage for unauthenticated rejection, default-off false, enabled-without-allowlist false, practice allowlist true/scoped, user allowlist true/scoped, malformed allowlist ignored/fail-closed, and no appointment/audit/provider calls. 6. Keep existing dev fixture/query-gated review tests passing and avoid changing response contracts unless the new endpoint requires only additive schema code.

## Visual / Behavioural Acceptance Checks

Behavioural checks: the endpoint is invisible to anonymous users; default config returns eligible=false; explicit non-PHI practice or user allowlist returns eligible=true only for that authenticated staff/practice; cross-practice users remain ineligible; malformed config fails closed; existing Bernie dev fixture and supervised booking routes keep their current contracts. Verification after implementation: python -m py_compile app/config.py app/services/bernie_pilot_gate.py app/routers/appointments.py app/schemas/appointments.py; pytest tests/test_bernie_staff_pilot_gate.py tests/test_bernie_dev_fixtures.py tests/test_bernie_supervised_booking_wrapper.py -q; source assertions/no-write counts prove no appointment writes, no audit writes, no LLM/provider calls; git diff --check.

## Risks / Ambiguities

Main ambiguity is whether Ariadne prefers the eligibility signal as a standalone endpoint or as an additive field on existing Bernie review payloads; I recommend a standalone endpoint because it avoids invoking proposal routes and keeps frontend gating independent. Another risk is role breadth: I will use existing staff appointment roles unless Codex narrows this during plan review. I will not implement until explicit complete sprint task approval.

## Codex Plan Review

- Review result: Accepted by Ariadne; implementation released to Codex worker.
- Required changes before implementation: None.
- Approved to proceed: yes
