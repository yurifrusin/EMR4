# Ariadne agent error and correction register — revision 518

Date: 2026-08-19

Timestamp: 2026-08-19T04:37:32.9752761+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 517

AER-0599 records recurrence of a stale closeout latch fixture. The kernel plan
test correctly retained the immutable preplanning receipt source but
incorrectly required the mutable live latch to remain at that opening source.
The integrated packet failed only that assertion after reaching 100 percent.

The repaired test binds the historical receipt exactly and validates the live
latch structurally: full lowercase 40-character source, schema-valid state and
operation-specific protected boundaries only while that operation remains
current. The kernel candidate and protected refs were unchanged.

## Register state

Revision 518 contains 599 bounded incidents. All are corrected or contained;
none is open. The closeout-fixture recurrence now binds AER-0319, AER-0402 and
AER-0599.

## Clockwork consequence

Immutable event receipts and mutable current projections are different clock
objects. The shared Ariadne/DeepSeek mechanism must generate tests that bind
the former to exact historical facts while validating the latter against its
current schema and causal position, eliminating predecessor literals from live
state assertions.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
