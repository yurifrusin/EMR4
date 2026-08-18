# Ariadne agent error and correction register — revision 528

Date: 2026-08-19

Timestamp: 2026-08-19T06:08:13.6850292+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 527

AER-0609 preserves a recurrence-composite identity mismatch. AER-0608 used the
correct Compass-staleness signature but independently reworded its resource
identity, so the generator correctly did not place it in the existing
recurrence row. The full register suite reported that one exact difference.

The correction restores the existing resource identity and regenerates the
pattern report before the complete suite is rerun.

## Register state

Revision 528 contains 609 bounded incidents. All are corrected or contained;
none is open. AER-0609 is the first occurrence of
`orchestrator.agent_error_register_recurrence_composite_resource_mismatch`.

## Clockwork consequence

A recurrence is a typed composite, not a prose label. The clockwork register
projector must select the canonical composite once and derive origin, category,
role, resource and signature together.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
