# Ariadne agent error and correction register — revision 541

Date: 2026-08-19

Timestamp: 2026-08-19T07:39:24.5770151+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 540

AER-0627 preserves the first closeout updater's prospective validation failure.
The draft used latch vocabulary `revision_required` as a Continuity decision
state, whose controlled states are `candidate`, `accepted` and `rejected`.
Validation failed before any graph, Compass or report write.

The correction uses decision state `rejected` and retains revision-required as
the narrative candidate disposition.

## Register state

Revision 541 contains 627 bounded incidents. All are corrected or contained;
none is open. AER-0627 adds recurrence signature
`agent.continuity_decision_used_latch_status_vocabulary`.

## Efficacy consequence

The final closeout reading is eleven failure-induced reruns, a 21.429 percent
reduction against fourteen. The candidate remains rejected and no reviewer or
provider is dispatched.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
