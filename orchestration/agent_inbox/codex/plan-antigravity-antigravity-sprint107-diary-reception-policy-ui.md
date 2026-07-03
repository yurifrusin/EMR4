# plan-antigravity-antigravity-sprint107-diary-reception-policy-ui

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint107-diary-reception-policy-ui` |
| Status | accepted |
| Created | 2026-07-03 14:06 +1000 |
| Source HEAD | `ece402f` |

## Plan Summary

Consume backend reception_policy in Diary Bernie panel for correct messaging

## My Understanding

The goal is to consume the backend reception_policy in the Diary Bernie review panel to prevent rendering incorrect or contradictory messages. We want to distinguish true slot-search failures from roster unavailability or other states. We must also ensure that advisory warnings like existing_future_follow_up do not block candidate slot display, and that stale/older response fallbacks remain safe and stable.

## Intended Surface / Boundary

We are modifying the Diary Bernie review panel, specifically how it renders status, headlines, and actions in docs/diary/diary.js. This affects the review panel content section and elements like statusBadge and headline. Adjacent components like the diary grid, booking modal, and instruction input must remain unaffected.

## Out Of Scope

Backend API/schema changes, database migrations, broad state-machine rewrite, persisted sessions, limited Bernie auto-mode, patient-specific copy branches, and changing booking/confirmation behavior.

## Files I Expect To Edit

docs/diary/diary.js, docs/diary/diary.css, review/test_diary_smoke.py

## Implementation Steps

1. Update bernieReviewTransition in docs/diary/diary.js to parse payload.reception_policy. 2. Set canShowNoSlots based on policy.search_ran_no_candidates === true, fallback to legacy rules if policy is absent. 3. Set canShowCandidates to policy.can_offer_candidates === true && candidateSlots.length > 0, fallback to legacy rules if policy is absent. 4. Map state to roster_unavailable when policy.availability === 'roster_unavailable'. 5. Update bernieStatusCopyForPayload and bernieHeadlineCopyForPayload to return 'Roster/schedule unavailable' when state is 'roster_unavailable'. 6. Update bernieReviewActionCopy to return 'I could not find a bookable session for that request...' when state is 'roster_unavailable'. 7. In candidate slots rendering block, handle empty slots for roster_unavailable state by showing 'There is no bookable session configured for that request.' 8. In docs/diary/diary.css, add style class .bernie-status-badge.roster_unavailable styled as a neutral grey badge. 9. Write Playwright smoke tests in review/test_diary_smoke.py to assert correct rendering of search_ran_no_candidates, roster_unavailable, advisory warnings, and stale/older fallback payloads.

## Visual / Behavioural Acceptance Checks

- Running pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q passes without errors. - node --check docs/diary/diary.js runs cleanly. - The UI correctly displays 'Roster/schedule unavailable' status and headline, and does not show 'No matching times found' unless reception_policy.search_ran_no_candidates is true. - Candidates list renders successfully when advisory warning existing_future_follow_up is present in the response.

## Risks / Ambiguities

Ensuring legacy payloads (which lack reception_policy) fall back gracefully without JavaScript runtime exceptions. This is mitigated by defensive checks (e.g. const policy = payload.reception_policy) and using existing logic when policy is falsy.

## Codex Plan Review

- Review result: Accepted with Codex/Dalton amendments: make `reception_policy` authoritative when present, keep older-response fallback, and prove the five message invariants in the Diary review harness.
- Required changes before implementation: Ensure advisory future-booking candidate-list assertion runs with auto-preview disabled so it tests candidate rendering rather than the auto-preview branch.
- Approved to proceed: yes
