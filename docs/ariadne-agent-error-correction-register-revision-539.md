# Ariadne agent error and correction register — revision 539

Date: 2026-08-19

Timestamp: 2026-08-19T07:18:30.9672439+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 538

AER-0625 preserves the first focused suite after the efficacy rejection. Four
tests still assumed the live reading was accepted: one asserted eight reruns
were at most seven and three tried to exercise accepted publication with the
rejected live efficacy object.

The correction derives a separate zero-retry synthetic generation for atomic
publication mechanics, makes the live assertion a generic threshold relation,
and has the publisher recompute efficacy so a caller cannot flip acceptance.

## Register state

Revision 539 contains 625 bounded incidents. All are corrected or contained;
none is open. AER-0625 adds recurrence signature
`repository.publication_tests_retained_live_acceptance_after_efficacy_rejection`.

## Efficacy consequence

The final candidate cost is nine failure-induced reruns, a 35.714 percent
reduction against fourteen. The rehearsal remains revision-required and cannot
publish an accepted generation or dispatch its reserved Gemini veto.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
