# Ariadne agent error and correction register — revision 529

Date: 2026-08-19

Timestamp: 2026-08-19T06:08:13.6850292+10:00 (Australia/Brisbane)

Status: accepted correction and containment update

## Change from revision 528

AER-0610 preserves one remaining duplicated population literal. Revision 528
advanced the aggregate agent-origin count to 428 but left the separate
`len(agent_incidents)` assertion at 427. The complete register suite reported
that one failure and all remaining tests passed.

The correction advances standalone and aggregate populations plus the affected
recurrence rows in one change before the full suite is rerun.

## Register state

Revision 529 contains 610 bounded incidents. All are corrected or contained;
none is open. AER-0610 recurs under
`orchestrator.agent_error_register_population_fixture_update_incomplete`.

## Clockwork consequence

The same population must not be independently copied into direct and aggregate
assertions. The clockwork reducer must emit both from one journal reading or
the workflow will continue manufacturing corrective reruns.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
