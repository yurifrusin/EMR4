# Ariadne agent error and correction register — revision 527

Date: 2026-08-19

Timestamp: 2026-08-19T06:08:13.6850292+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 526

AER-0608 preserves the four expected-value failures exposed after the valid
Continuity 327 / Compass 309 advance. The dedicated architecture Continuity
test passed, but two global baton assertions, the previous-next-tranche
boundary assertion and the global Compass node sentinel still named Continuity
326 / Compass 308, the kernel node and the architecture tranche.

The correction binds all four fixtures to the same prospective navigation
projection and reruns the exact closeout packet.

## Register state

Revision 527 contains 608 bounded incidents. All are corrected or contained;
none is open. AER-0608 recurs under
`repository.compass_current_position_literal_stale_after_valid_advance`.

## Clockwork consequence

Navigation literals are projections of one acknowledged tick. The clockwork
must emit the dedicated Continuity test, live baton assertions and global
Compass sentinel from that same projection before any canonical publication.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
