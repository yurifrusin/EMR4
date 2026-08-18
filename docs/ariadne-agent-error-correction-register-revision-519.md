# Ariadne agent error and correction register — revision 519

Date: 2026-08-19

Timestamp: 2026-08-19T04:37:32.9752761+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 518

AER-0600 records another occurrence of the stale mutable-latch fixture. After
the kernel operation validly transitioned to `complete`, the generic latch
continuity test required its fallback operation to be one historical
post-native-Harness closeout. The focused transition packet passed 64 checks
and failed only that literal assertion.

The repaired fallback accepts any schema-valid completed current operation,
requires a full lowercase 40-character source and a non-empty completed stage,
and retains exact facts only for recognised immutable historical transitions.
The terminal reason is also aligned with the canonical `operation_complete`
projection. Product source and protected refs were unchanged.

## Register state

Revision 519 contains 600 bounded incidents. All are corrected or contained;
none is open. The closeout-fixture recurrence now binds AER-0319, AER-0402,
AER-0599 and AER-0600.

## Clockwork consequence

This second closeout rerun is direct efficacy evidence for the proposed
mechanism: mutable current-state tests must be generated from typed terminal
events, while exact historical claims belong to immutable receipts. Removing
hand-maintained fallback identities is an explicit target measurement, not an
additional ceremony.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
