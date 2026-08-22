# Check-in prospective-success redaction and typed cleanup-projection conformance repair

Date: 2026-08-23

Status: `candidate_passed`

Exact reviewed implementation source:
`8a82a8184cc66efbe31769eda88e299887f798bc`

## Result

The two diagnosed failure coordinates are repaired without an occupied run.

The base harness now constructs the complete prospective success-evidence
projection during static admission. Its 67 normalized key paths exactly match
the 67 runtime-result paths, the complete projection passes the unchanged
redactor and evidence schema, and all 66 exact/prefix/suffix hostile forbidden-
field mutations fail closed before the first Docker-capable call.

The sole conflicting boundary was renamed from
`live_secret_existing_hosted_or_product_database_used` to
`live_sensitive_material_existing_hosted_or_product_database_used`. The ten-
field boundary remains closed and every value remains `false`. The forbidden-
key vocabulary and redactor AST are unchanged from accepted diagnosis source
`ca7970b3520b2c38e9abd6fee3462ebb743792e0`.

The base harness now owns a frozen `PostFinalizationTerminal` and one terminal
bridge after cleanup. Deterministic cases prove that:

- late `redaction/forbidden_field` becomes typed failure evidence with the
  exact finalized `cleanup_verified` projection;
- late `evidence/parent_schema_invalid` does the same;
- rejection of contaminated failure evidence produces a bounded fallback while
  preserving `cleanup_incomplete`;
- a valid candidate writes only the attestation/success pair; and
- the historical attempt-007 wrapper projects the base-owned
  `cleanup_verified` value rather than inventing `not_started`.

No intended late failure escaped and no success was released after a late
failure.

## Efficacy reading

The accepted diagnosis recorded one forbidden-field escape that consumed an
occupied attempt and one subsequent cleanup-projection collapse. The repaired
deterministic reading is zero and zero, using zero occupied runs. These are not
new narrative checklist items: both controls are executable gears on the
actual base-harness path.

The honest build cost is 259 net lines in the reusable base harness plus 1,063
lines of closed contract, schema, conformance runner and focused tests. That is
substantial, but its payoff is recurrent: every future invocation of this base
harness receives the projection gate and typed terminal bridge without a new
manual form or per-attempt repair.

## Evidence boundary

Canonical deterministic evidence is `repair-evidence.json`, SHA-256
`47f422e7b8ad072c9f4912fe6269cfc85f44eb75808419182c75e19d41157eaa`.
It records zero Docker objects, PostgreSQL starts, SQL/database operations,
provider calls, product calls and attempt-008 actions. Attempt 007 remains
byte-exact, consumed once, retried zero times and unreclassified.

This repair proves structural admission and terminal projection only. It does
not prove rollback, unknown-response transaction recovery, role absence before
teardown or any successful occupied database behavior. Attempt 008 remains
closed pending its own fresh authority and frozen plan.
