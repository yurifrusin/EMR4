# Ariadne agent error and correction register — revision 521

Date: 2026-08-19

Timestamp: 2026-08-19T04:37:32.9752761+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 520

AER-0602 preserves a regression-test literal mismatch. The complete-state
integrated packet reached 100 percent and failed only because the new AER-0600
test asked for `typed terminal events`, while the canonical prevention control
says `terminal event schema`.

The register control remains unchanged. The test now reads the exact canonical
wording. Candidate and protected refs were unchanged.

## Register state

Revision 521 contains 602 bounded incidents. All are corrected or contained;
none is open. AER-0602 is the first preserved occurrence of this exact
regression-assertion literal signature.

## Clockwork consequence

Regression assertions are another projection: they should be derived from
typed canonical fields or exact stored control values, not rephrased by hand.
This rerun is included in the clockwork efficacy baseline.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
