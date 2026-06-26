# plan-codex-codex-bernie-confirm-create-proposal-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-confirm-create-proposal` |
| Branch | `codex/bernie-confirm-create-proposal` |
| Source Task | `codex-bernie-confirm-create-proposal-contract` |
| Status | pending_plan_review |
| Created | 2026-06-27 00:39 +1000 |
| Source HEAD | `07218d0` |

## Plan Summary

Plan backend-only Bernie confirmation create-proposal bridge

## My Understanding

Role: codex-worker. Worker Name: Cicero. Worker Branch: codex/bernie-confirm-create-proposal. After explicit `complete sprint task` approval only, add the supervised backend confirmation bridge that consumes already-approved Bernie slot-selection/create-proposal evidence and turns it into exactly one appointment write when, and only when, the caller provides explicit bounded confirmation. The bridge must preserve existing auth, practice scoping, conflict safety, and proposal checks; write bounded audit evidence identifying the supervised Bernie/proposal source; and perform no Gemini/LLM/provider calls or autonomous natural-language execution.

## Intended Surface / Boundary

Backend appointments confirmation/write API only, likely a typed route/helper under app/routers/appointments.py plus schemas in app/schemas/appointments.py. The affected behavioural surface is a staff-confirmed API contract: explicit confirmation in, appointment/audit write out on success, blocked response/no write on failure. No diary card, booking slot visual, stacking, panel, waiting room, diary grid, taskpane, Command Centre, or UI surface changes; adjacent normalized slot-search, slot-selection proposal, create-proposal, and Sprint 43 harness behaviours must remain compatible.

## Out Of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing or calls, autonomous Bernie runtime, direct natural-language execution, SMS, billing, resource admin, migrations unless strictly unavoidable, broad appointment redesign, broad audit framework redesign, unrelated test hygiene, and any mutation path that does not require explicit confirmation.

## Files I Expect To Edit

Expected after approval: app/schemas/appointments.py for confirmation request/response schemas; app/routers/appointments.py for a narrow confirmation route/helper that reuses existing create-proposal/create appointment safety logic; focused tests, likely tests/test_bernie_confirm_create_proposal.py or adjacent appointment proposal tests, to prove success and blocked/no-write cases. Possibly touch existing Sprint 42/43 tests only for compatibility assertions. No production code, tests, migrations, docs, or UI files during this plan-gate turn.

## Implementation Steps

1. Inspect existing Sprint 40-43 Bernie normalizer, normalized slot-search, slot-selection proposal, create-proposal, appointment create, conflict, auth/practice, and audit patterns. 2. Define a small confirmation schema that requires explicit confirmation and carries bounded supervised proposal evidence/source identifiers, rejecting missing/false confirmation. 3. Implement the narrow backend route/helper so it revalidates practice/auth/conflict/proposal safety at confirmation time, creates exactly one appointment inside the success path, and returns a deterministic blocked response without writes otherwise. 4. Add bounded audit semantics that identify the supervised Bernie/proposal source without logging large free text, raw LLM content, or unrelated patient data. 5. Add focused tests for missing confirmation, stale/mismatched/blocked proposal evidence, conflict failure, auth/practice scope failure, successful exactly-one appointment write, bounded audit evidence, and no LLM/provider calls. 6. Run py_compile for touched Python, focused confirmation pytest, Sprint 43 flow harness, adjacent slot-selection/create-proposal tests, and git diff --check before submit.

## Visual / Behavioural Acceptance Checks

Plan-gate acceptance: this packet states Role codex-worker, Worker Name Cicero, Worker Branch codex/bernie-confirm-create-proposal, and backend-only scope. Post-approval behavioural acceptance: an unconfirmed or unsafe request creates no appointment and no audit rows; a safe explicitly confirmed request creates exactly one appointment and one bounded audit evidence trail; auth/practice/conflict checks remain enforced; existing Bernie normalize-search-select/create-proposal harnesses still pass; no Gemini/LLM/provider path is imported or called; no UI/diary/taskpane/Command Centre behaviour changes.

## Risks / Ambiguities

Need to avoid treating proposal evidence as authorization by itself; confirmation must be explicit and revalidated. Need to avoid duplicate appointment writes on retries or ambiguous success states; if idempotency is not already available, scope the smallest deterministic duplicate guard or return shape for Ariadne review before coding. Need to find the existing audit model/route pattern that can hold bounded source evidence without a broad audit redesign. Need to ensure tests prove no writes on every blocked path, not only response status.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
