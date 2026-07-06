# R27 Receptionist Acceptance Review: H-Series Profile Consumption

Date: 2026-07-06
Status: source-safe acceptance criteria

## Acceptance Position

H-series neutral profiles are acceptable for receptionist-facing regression work
only as boundary evidence. They may remind the project that historical diary
movement exists and that EMR4 must preserve backend authority during refresh and
confirmation flows. They must not be treated as evidence that a real appointment
was created, moved, cancelled, extended, checked in, or handled by a particular
staff member.

## Accepted Test Shape

Receptionist acceptance is satisfied when tests prove:

- H-series profiles carry an explicit schema version.
- H-series profiles remain outside executable Bernie scenario fixtures.
- Bernie scenarios do not reference H-series profile ids.
- Profile metadata cannot silently become scenario parameters.
- The H15 semantic labelling gate remains closed.

## Rejected Test Shape

Receptionist acceptance is not satisfied by tests that:

- rename neutral movement into appointment intent;
- load H-series profile data into Bernie replay;
- use `deterministic_uses` as a machine permission switch;
- claim a neutral event class means a real-world receptionist action occurred;
- send profile data to a provider prompt or external model.

## Product Direction

The next useful product step is native Bernie/Diary action grammar, not more
semantic inference from the trove. H-series profiles can support the safety
rails around that work, while the full trove waits for a reviewed H15/full-trove
gate.
