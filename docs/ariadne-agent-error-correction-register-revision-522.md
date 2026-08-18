# Ariadne agent error and correction register — revision 522

Date: 2026-08-19

Timestamp: 2026-08-19T05:20:02.5485051+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 521

AER-0603 preserves a pre-existing transactional-shadow fixture defect. Four
accepted transactional tests replayed one immutable historical manifest while
reading the unrelated mutable live operation latch. The valid clockwork-gear
successor transition therefore stopped them at `active_operation_mismatch`.
The broker, latch, Git-object and preflight suites passed.

The corrected test derives a provider-free fixture latch from the live latch's
validated structure while binding its operation identity to the immutable
manifest. The live latch remains unchanged and authoritative for current work;
the historical fixture no longer depends on mutable current identity.

## Register state

Revision 522 contains 603 bounded incidents. All are corrected or contained;
none is open. AER-0603 is the first repository-origin occurrence of
`repository.immutable_shadow_fixture_bound_to_mutable_live_latch` and is the
fifth observed stale mutable-projection event in the broader workflow history.

## Clockwork consequence

Historical replay fixtures and mutable live projections require different
gears. The former derives from its immutable manifest/event receipt; the latter
is validated structurally at the current journal tip. The proposed clockwork
must generate that relationship rather than leaving a global live-state read in
an immutable test.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
