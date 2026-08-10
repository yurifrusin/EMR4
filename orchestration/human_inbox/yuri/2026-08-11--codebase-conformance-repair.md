# Tranche closeout — codebase conformance repair

Date: 2026-08-11

Result: `passed`

Yuri attention required: `no`

## Lay summary

Raisa's development safety net now has a reliable guest list. The repository
states exactly which current Python files must compile as Python 3.11, and the
protected CI check can no longer quietly skip those files. Old API maps also
no longer overrule what has since been built: the practitioner directory is
correctly recorded as an existing read-only surface, while the four genuinely
unbuilt read areas remain closed.

A separate compass check now catches the kind of stale handover sentence that
could send development back toward already completed work. No patient-facing
or staff-facing behavior changed.

## Technical summary

- Added `python_source_state.json` plus a fail-closed validator selecting 202
  maintained files without enumerating protected evidence.
- Added exact Python 3.11 runtime enforcement, in-memory compilation, Ruff and
  a 92-test static no-conftest packet to protected Python CI.
- Preserved the historical five-row API gap inventory and added a current
  five-surface lifecycle/schema pair.
- Added current baton/Continuity/Compass/master-plan consistency checks.
- Removed one unused import; made no functional product-source change.
- Passed 30 focused conformance checks, the 98-test canonical fast profile and
  117 focused API/practitioner lifecycle checks.

## Issues revealed

The first pass caught an unused test import, the handover's compactness ceiling
and a clean-CI dependency trap caused by pytest's automatic database conftest
loading. All three were repaired inside the frozen scope. Exact Python 3.11
execution will occur on the protected workflow runner; local evidence uses
Python 3.14 compilation plus Ruff's exact `py311` parser and a runtime-mismatch
guard.

## Deliberately still closed

Protected evidence, historical Diary PHI, patient/clinical/product data,
providers, database behavior and migration execution, watchers/sources, tools,
commands, credentials, deployment, production, release, Pages and protected
refs remain closed.

## Place in the Raisa direction

This is preventive structural maintenance before Raisa gains an execution
surface. It makes the code/body boundary more legible and mechanically keeps
historical maps, current implementation and the development baton from
silently drifting apart.

## Planned next tranche

Begin AES-C0 architecture and contract: define the external containment broker,
capability classes, immutable per-generation manifest, exact denial/fallback
states and the separation between reads, model reasoning and human-gated REST
commands. This remains architecture-only and provider-free. No intervention is
needed.
