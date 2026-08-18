# Ariadne agent error and correction register — revision 524

Date: 2026-08-19

Timestamp: 2026-08-19T05:20:02.5485051+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 523

AER-0605 preserves one rejected regression assertion. The new AER-0604 test
used a paraphrase that did not occur in the canonical prevention-control text,
so the full register suite correctly failed its final assertion. Canonical
register validation and all preceding tests passed.

The correction asserts an exact stored phrase, preserves the failed packet and
reruns generation plus the complete register suite.

## Register state

Revision 524 contains 605 bounded incidents. All are corrected or contained;
none is open. AER-0605 recurs under
`orchestrator.agent_error_register_regression_assertion_literal_not_canonical`.

## Clockwork consequence

This is another direct example of copied prose creating work without adding
assurance. The clockwork must project regression predicates from typed fields
or exact stored controls instead of requiring a second manually remembered
wording.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
