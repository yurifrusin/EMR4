# Ariadne agent error and correction register revision 150

Date: 2026-08-10

Status: corrected

Revision 150 adds AER-0176 and brings the register to 176 bounded incidents
with zero open incidents.

## AER-0176 — inert descendant retained predecessor body digest

The full inert-DDL packet passed 87 tests and failed one: the representability
recovery test still expected the predecessor body digest after the accepted
policy-only structural rebind. The canonical current body digest is
`sha256:edbc7f2361f8b5a2812dcff2a7cdf81bef7bd2a6d280be5a9023571c5121508e`;
all typed body programs and effective population remain unchanged.

The test now binds the current digest while retaining all of its independent
population and semantic assertions. Future body-parent rebind packets must
search the exact inert-DDL descendant cohort for the predecessor digest before
execution eligibility.
