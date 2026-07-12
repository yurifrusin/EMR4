# EMR4 S5 Receptionist Workflow Audit Closeout

Date: 2026-07-12
Status: complete

S5 exercised the Word taskpane-to-diary workflow through the first real Ariadne
product sprint. D-1 completed the frontend trace, D-2 completed the backend
contract audit, and A-1 returned a Conditional Go usability verdict.

Fable selected one pre-authorized repair: preserve `.appt-active` appointment
selection when the 60-second silent refresh rebuilds the diary grid. D-1 added a
focused Playwright regression test and the frontend fix; D-2 cross-review passed.

Final evidence:

- `review/test_diary_selection_preservation.py`: 3 passed.
- `node --check docs/diary/diary.js`: passed.
- `review/test_diary_smoke.py`: unchanged baseline of 8 known failures; no B-1
  regression.
- Full `pytest tests -q` is not currently a clean project-wide signal because
  of numerous pre-existing static-readiness/environment failures; it was not
  represented as passing.

Deferred findings:

- Terminal appointment statuses can be changed back to active statuses through
  raw PATCH. Behavior is confirmed, but block/warn/allow is an undelegated
  product-policy decision and was not changed.
- Eight diary smoke failures reflect GraphQL mock and smoke-mode assertion
  drift. This is the leading bounded EMR4 follow-up.
- Other A-1 and D-2 findings remain recorded in their lane artifacts.

No S5 work opened Bernie D5, provider, memory/RAG, historical diary runtime,
deployment, external-client, schema, or new write-authority gates.
