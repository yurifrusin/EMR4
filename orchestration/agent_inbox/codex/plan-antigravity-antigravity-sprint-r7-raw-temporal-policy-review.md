# plan-antigravity-antigravity-sprint-r7-raw-temporal-policy-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-r7-raw-temporal-policy-review` |
| Status | pending_plan_review |
| Created | 2026-07-05 17:05 +1000 |
| Source HEAD | `e7e891f` |

## Plan Summary

Draft receptionist-domain and product policy review of raw appointment temporal guards in app/routers/appointments.py.

## My Understanding

Under Sprint R7, we must review temporal validation policies for raw appointment mutation paths (such as direct create/update/status-patch/delete routes in app/routers/appointments.py) versus Bernie's proposal/conversational paths. Raw routes currently lack the strict past-date blocks or same-day window clarifications present in the Bernie/supervised paths. We need to define which raw paths should hard-block, clarify, or remain compatibility-only, and provide test-design recommendations.

## Intended Surface / Boundary

Documentation only: docs/receptionist_review_r7.md will contain the completed policy review and inventory.

## Out Of Scope

No production code changes, test suite changes, database migrations, Word taskpane edits, or live provider calls. No changes to the actual receptionist_review_r7.md file during the planning phase.

## Files I Expect To Edit

docs/receptionist_review_r7.md

## Implementation Steps

1. Read and analyze the raw vs. proposal appointment routes in app/routers/appointments.py.
2. Formulate a policy mapping for temporal constraints on direct create/update/delete/status routes versus proposal confirm paths.
3. Outline the compatibility/import safety boundaries and staff override scenarios.
4. Design deterministic test cases using mock times/headers to verify temporal policies on raw paths.
5. Draft the complete review document in docs/receptionist_review_r7.md during the implementation phase.

## Visual / Behavioural Acceptance Checks

A structured markdown document at docs/receptionist_review_r7.md that: (a) inventories all raw and proposal routes in app/routers/appointments.py; (b) classifies each route's safety policy (hard-block, clarify, or compatibility-only) with clinical/operational rationale; (c) provides clear test designs for raw path temporal policies.

## Risks / Ambiguities

1. Backward compatibility and data migration/import: Hard blocks on raw paths could prevent seeding or importing historical records unless an explicit compatibility/system-level override exists.
2. Clinic operational override: Staff may legitimately need to record past events (retrospective logging). Hard-blocking raw UI paths without clear UX escape routes could disrupt workflow.
3. Timezone/local-time differences across practices.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
