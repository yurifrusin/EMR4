# Bernie Scenario Spec Fixtures

This directory contains the canonical LC1 semantic-coverage scenarios as
`ReceptionScenarioSpec` JSON documents.  Each fixture describes one scenario
for the Bernie reception-agent coverage lattice: the original dialogue, the
expected temporal/practitioner/patient semantics, and the outcomes that must
or must not occur.

## Provenance

The fixtures in this directory are **adapted from authored T1/T2 golden
scenarios**.  T1 and T2 scenarios were written by the Sol (Conductor) as
deterministic scenario-memory and interpret/confirm route-contract fixtures.
They have been adapted to the `ReceptionScenarioSpec` schema defined in
`app/services/bernie/scenario_spec.py`.

## Tier

**Gold (independently adjudicated).** A Gold scenario has a clear structured
specification and is derived from a known real conversation pattern or a
hand-authored curated scenario. These three worker-authored adaptations were
checked against their named committed T1/T2 sources by the protected Sol
integrator. Generated additions must preserve that author/judge separation.

## Adjudication Authority

**Sol (Conductor)** is the sole adjudication authority for scenario-tagging
decisions.  Adjudication means Sol has reviewed the fixture, confirmed its
semantic labels match the original T1/T2 intent, and that any boundary
decisions are recorded.

## Family Labels

| Family | Meaning |
|---|---|
| `booking_create` | Scenarios where the receptionist requests a new appointment booking |
| `clarify_temporal` | Scenarios that require temporal-bounds clarification |
| `booking_move` | Scenarios where an existing booking is moved to a different time |
| `booking_resize` | Scenarios where an existing booking's duration changes |
| `booking_cancel` | Scenarios that cancel an existing booking |
| `status_change` | Scenarios that update the lifecycle status of a booking |
| `explain_schedule` | Scenarios requesting an explanation of the schedule |
| `adversarial` | Scenarios testing edge cases or incorrect input handling |

## How to Add New Scenarios

1.  Create a new JSON file in this directory.
2.  Ensure it satisfies the `ReceptionScenarioSpec` schema.
3.  Add corresponding tests in `tests/test_bernie_scenario_spec.py`.
4.  Run `scripts/bernie_coverage_lattice.py` to verify the new scenario
    fills one or more empty cells in the coverage lattice.
5.  If the scenario is from a real conversation, set `provenance` to
    `silver` or `bronze`.  For hand-authored curated scenarios, use `gold`.

## Gold vs Silver vs Bronze

| Tier | Definition |
|---|---|
| **Gold** | Authored from curated evidence; fully specified and independently adjudicated |
| **Silver** | Derived from synthetic replay or mutation of a Gold fixture; partial field coverage acceptable |
| **Bronze** | Extracted from real-world interaction notes or historical logs; may have missing fields; must not contain PHI |
