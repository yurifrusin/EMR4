# LC4R9 Generator-backed Contract Repair

## Summary

The LC4R9 sprint implements a fail-closed source-generator allowlist that overrides
the expected audit delta vocabulary from `create_requested` to `created` for exactly
11 surface scenarios whose replay contract already produces `created`.

## Frozen repair selection

The following 11 surface scenarios are repaired from `create_requested` to `created`:

| Scenario ID | Group | Variant |
|---|---|---|
| `lc4_dw1_dev_var_001_01` | 001 | 01 |
| `lc4_dw1_dev_var_001_02` | 001 | 02 |
| `lc4_dw1_dev_var_001_03` | 001 | 03 |
| `lc4_dw1_dev_var_001_05` | 001 | 05 |
| `lc4_dw1_dev_var_001_06` | 001 | 06 |
| `lc4_dw1_dev_var_001_07` | 001 | 07 |
| `lc4_dw1_dev_var_001_08` | 001 | 08 |
| `lc4_dw1_dev_var_001_09` | 001 | 09 |
| `lc4_dw1_dev_var_012_03` | 012 | 03 |
| `lc4_dw1_dev_var_012_05` | 012 | 05 |
| `lc4_dw1_dev_var_012_07` | 012 | 07 |

Selection count: 11
Selection hash: `b88018991e49ffd5`

## Implementation

### Source generator allowlist

Added to `app/services/bernie/scale_corpus.py`:

- `LC4R9_AUDIT_VOCABULARY_ALLOWLIST` — frozen set of the 11 scenario IDs
- `LC4R9_ALLOWLIST_SELECTION_HASH` — `b88018991e49ffd5`
- `LC4R9_ALLOWLIST_COUNT` — 11
- `LC4R9_AUDIT_OVERRIDE` — a tuple containing the canonical read-only audit
  mapping for `created`, `apt-001`, count 1
- `_make_audit_override_copy()` — returns a fresh list/dict copy for each
  generated scenario
- `LC4R9_PRE_REPAIR_DELTA_HASH` — SHA-256 of sorted `scenario_id|create_requested|created` lines
- `_validate_lc4r9_allowlist()` — fail-closed validation of hash, count, surface-only constraint

### Generator integration

In `_build_group_fixture`, when building each surface variant, the code checks whether
the `variant_id` is in the allowlist. If so, it asserts the action is `create` and
passes a fresh canonical override copy as `expected_audit_deltas_override` to
`_build_scenario`.

### Fixture regeneration

Groups 001 and 012 (the only groups containing allowlist scenarios) were regenerated
through `generate_development_fixture`. The manifest was updated with new group hashes
and the cascading corpus hash. All other 94 group files are byte-for-byte identical to
their committed state.

## Post-repair state

- All 11 selected scenarios have `expected_audit_deltas` = `[{"change_type": "created", "appointment_id": "apt-001", "count": 1}]`
- All non-selected create scenarios retain `create_requested`
- `_derive_audit_deltas` globally unchanged
- Group 001 hash: `sha256:b1e33767b127856e25095c907b14a40a6f88e6522af0cc1841e9baa3bdeff6d7`
- Group 012 hash: `sha256:90d321501e51df4e1b91aa94997e3470b3d26c2678ca61045ad8c6c63abdc5c0`
- Corpus hash: `sha256:f11e98f9bc61b962da0e816fbb918d7f722d3f82c57dfde18a5e323c1b24e9e1`
- Generator repair remaining: 0
- Clarification blockers: 53
- Replay contract-reconciliation blockers: 40
- Exit status: `blocked_pending_contract_reconciliation`

## Verification

- 54/54 focused tests pass
- `scripts/bernie_lc4r9_generator_contract_repair.py --check` passes
- Python compilation passes for all 3 owned modules
- Byte-for-byte full regeneration check passes
- `git diff --check` is clean
- Product/corpus changes remain limited to the 9 worker-owned files; Sol's
  separate recovery amendment records acceptance provenance
- Real two-repeat evaluator evidence preserves semantic counts
  `880/814/628/101/300/782`, safety 1,152/1,152, and zero variance over 2,304
  samples
- Frozen LC4R8 development-only selections recompute to zero generator-repair
  cases, 53 clarification blockers, and 40 remaining replay reconciliation
  blockers
