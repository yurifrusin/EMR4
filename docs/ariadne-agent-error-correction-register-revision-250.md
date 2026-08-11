# Ariadne agent error and correction register — revision 250

Date: 2026-08-12

Revision 250 records and corrects AER-0282. The register now contains 282
bounded known incidents with none open.

The first CF-D2 recovery diagnostic passed its ten setup preconditions and
position-one atomic transition, then isolated the failure at the immediately
following lifecycle anchor. Registration creates a revision-zero baseline;
position one advances the checkpoint to lifecycle revision one; and the
accepted anchor entry point accepts only that current revision. The harness
and frozen prose incorrectly requested numeric revision two before position
two was allowed to apply.

The single bounded correction passes lifecycle revision one while retaining
`append_anchor_2` as the ordinal name of the second anchor after the baseline.
It changes no accepted SQL, authority, RLS, transaction, durability,
classification or fencing meaning. A new deterministic test binds the harness
argument to the exact inert SQL lifecycle arithmetic, and a fresh exact-HEAD
review remains mandatory before diagnostic attempt 002.

This incident is also evidence for the later workflow diagnosis: several
layers repeated the phrase “revision two” without mechanically reconciling it
to the executable lifecycle state machine. Strong process here means one
machine-checkable invariant at the contract boundary, not more prose repeating
the same unchecked assumption.
