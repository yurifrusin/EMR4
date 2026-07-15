# LC4V2R1 Entity/Normalization Repair

## Scope

Repair the deterministic extraction boundary to support the five canonical
entity slots — `patient`, `practitioner`, `location`, `appointment_type`,
and `duration` — with full semantics (`exact`, `omitted`, `ambiguous`,
`corrected`, `negated`) and lexical duration normalization.

## Baseline (pre-repair)

- Committed at source commit `7abf3aa9`
- 21-case frozen Sol-authored fixture
- 17/21 normalized-values passes
- 5/21 entity-semantic passes
- 17/21 clarification/authority/tool-safety passes
- 21/21 no-completion-claim passes
- 4/21 complete passes
- 17-case failure selection hash: `ddfbc280bb822993`

## Post-repair

- 21/21 across all seven contracted dimensions
- Zero repeat variance
- Canonical report hash:
  `sha256:46570a2e3ab5d47fe4d74594544d4e92f1d68cc8d8a51d5db39a233f59d84c38`
- Ordinary development corpus counts and hash unchanged
- Final serial preservation gate: 383 collected, 381 passed, one expected
  xfail, and one expected skip

## Changes

### `app/services/bernie/semantic_extraction.py`

1. **Location extraction** (`_extract_location`): Detects `Room <number>`
   (exact), `any room` (ambiguous), corrected via multi-turn, and explicit
   negation (`not in Room X`).

2. **Appointment type extraction** (`_extract_appointment_type`): Detects
   `standard consultation`, `long consultation`, `care plan appointment`
   (exact), ambiguous references, corrections, and explicit negation.

3. **Lexical duration normalization**: Maps `half an hour` → 30,
   `one hour` → 60, `a quarter of an hour` → 15 minutes.

4. **Entity negation detection**: Patient/practitioner/duration negation
   via direct `not [entity]` prefix check. Does not overmatch on
   action-level negation (`do not book X`).

5. **Duration negation in normalized_values**: Negated duration is removed
   from `normalized_values` output.

6. **Clarification for negated entities**: Negated/ambiguous patient,
   practitioner, or duration triggers `requires_clarification` for
   `create` action, with `clarify` authority and no mutation tools.

### `tests/test_bernie_lc4v2r1_entity_normalization.py`

- 21 parameterized per-case extraction tests
- Fixture integrity tests (hash, count, schema, unique IDs, relations)
- Forbidden expected-field injection tests
- False-positive entity capture protection tests
- Negated-action/entity scope and location-clause scope tests
- Appointment-type versus duration separation tests
- Immutable baseline and canonical report-hash mutation tests
- Temporal interval regression test (`after 3 but before 4:30`)
- Two-repeat zero-variance test

### `scripts/bernie_lc4v2r1_entity_normalization.py`

- Development-only audit harness with explicit `--write` mode and a
  non-mutating exact `--check` mode
- Produces `docs/bernie-lc4v2r1-entity-normalization-report.json`
- Reports baseline comparison, per-case findings, selection hashes,
  variance, canonical report hash, and protected-boundary declarations

## Worker and recovery provenance

DeepSeek V4 Flash/high supplied candidate commit `861049e9`. Sol rejected its
self-certified pass because the first audit checker rewrote its report, did not
bind the immutable baseline, retained an unset completion hash, and over-broadly
scoped one patient-negation pattern. Sol preserved the candidate and recovered
the evidence tooling and semantic scope under the Ariadne lease without a Flash
correction loop. See
`orchestration/agent_inbox/codex/lc4v2r1-sol-recovery-amendment.md`.

## Protected boundaries

- Holdouts v1 and v2: **sealed, not accessed**
- Provider calls: **none**
- Runtime/database writes: **none**
- T3.5: **deferred**
