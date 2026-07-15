# LC4R10 Sol Contract-Reconciliation Contract

## Authority and evidence boundary

GPT Sol owns this taxonomy, architecture, acceptance, recovery, and protected
integration. DeepSeek V4 Flash through Claude Code `--bare` may implement only
the bounded mechanical contract below. Gemini 3.5 Flash through a fresh
Antigravity context supplies the independent veto after Sol verification.

This sprint is development-only. Protected holdout v1 must not be opened,
enumerated, imported, loaded, regenerated, evaluated, hash-checked, inferred
from, or tuned against. T3.1-T3.4 remain intact and blocked by default; T3.5,
provider calls, routes, databases, UI, deployment, release, historical diary
material, and all live/write authority remain out of scope.

## Frozen populations

The authoritative inputs are the committed development-only LC4R8 audit
artifacts. Historical reports and fixtures must not be edited in place.

- Clarification population: 53 records, selection hash `9496e23c6f339603`.
- Replay population after excluding the 11 LC4R9-completed audit-vocabulary
  records: 40 records, selection hash `defe4c59877753e9`.
- Combined population: 93 unique records, selection hash
  `d8d138cb267b4304`.

Replay subpopulations:

- resolved reversal/no outcome: 1, `020fade8ca644684`;
- resolved correction/candidate selection: 1, `d67780b27dbfbdca`;
- T1-backed valid create-policy alignment: 14, `e79a4ecc777b9f9c`;
- fail-closed no-outcome contracts: 24, `2913bfd9110af319`.

Resolved-clarification action populations:

- create: 13, `1839c8c567e44922`;
- move: 13, `ec7e009f37f0834a`;
- resize: 14, `e49785ce6f8922e5`;
- cancel: 13, `830386f883de7fd0`.

Of those 53, the pre-policy profile contained 20 action outcomes and 33
fail-closed outcomes. Applying the separately frozen T1-backed create-policy
correction moves the selected `same_day_distinct` and terminal-history
dialogues into the action-outcome population, so the accepted post-correction
split is 22 (`e9b8e74b01d3ffc6`) and 31 (`73229d3e6f4a355c`).

## Canonical decisions

1. `expected_outcome_kind` becomes a required nullable contract field. An
   explicit JSON `null` means the deterministic replay must produce no
   downstream outcome. Omitting the field remains invalid. This preserves the
   distinction between an explicit no-outcome contract and missing evidence.
2. Reversal `lc4_dw1_dev_mt_001_03` is withdrawn: no outcome, search-only tool
   selection, and no appointment or audit delta.
3. Corrected overlap `lc4_dw1_dev_mt_003_02` is resolved rather than ambiguous:
   `candidate_selection_required`, ordinary create-path tool selection, and no
   appointment or audit delta.
4. Create replay may produce `appointment_created` for `empty`,
   `same_day_distinct`, and `terminal`. This is required by the committed T1
   stateful cases: same-day-distinct is not a duplicate and a terminal prior
   appointment does not masquerade as existing. `exact_duplicate` remains
   `existing_booking_found`; `overlap` remains
   `candidate_selection_required`; `stale`, `concurrent`, `roster_absent`,
   `break`, `no_slots`, and `elapsed_window` remain fail-closed with no outcome.
   Other actions retain their existing fail-closed uncertain-state policy.
5. The 53 `*_01` dialogues are resolved two-turn dialogues. Their second turn
   supplies the requested detail, so expected clarification is null, choices
   are empty, and the expected tool sequence is the ordinary action sequence.
6. Their semantic contracts come from the fixed authored templates:
   - create: `approximate`, tomorrow, `14:30`-`15:30`, 15 minutes, exact
     patient/practitioner/duration;
   - move: `exact`, tomorrow at `16:00`, exact patient/practitioner, duration
     omitted;
   - resize: `exact`, tomorrow at `15:00`, 30 minutes, exact
     patient/practitioner/duration;
   - cancel: `exact`, tomorrow at `15:00`, exact patient/practitioner, duration
     omitted.
   Source spans must be regenerated from those authored turns and the corrected
   values. Expected labels/source-span names must never be copied from the
   interpreter or scorer.
7. Selected scenarios with no outcome have empty appointment/audit deltas.
   Selected scenarios with an action outcome use the deterministic replay delta
   vocabulary (`created`, `moved`, `resized`, or `cancelled`) and the replay's
   canonical appointment-delta shape. Candidate-selection has no mutation
   delta. No global historical-report rewrite is authorized.
8. All changes are source-generator backed and full development-fixture
   regeneration must be byte-for-byte reproducible. Selection validation must
   fail closed on count/hash/type drift.

## Acceptance

- all 93 frozen records satisfy their corrected semantic, clarification,
  outcome, tool, appointment-delta, audit-delta, authority, and safety contract;
- the 14 valid-state create cases pass without weakening stale/concurrent or
  other fail-closed cases;
- every selected explicit-null outcome produces zero appointment/audit deltas
  and no simulated confirmed write;
- expected development semantic counts are independently recomputed rather
  than copied into the report;
- safety remains 1,152/1,152 and variance remains zero over 2,304 samples;
- the ordinary development generator, loader, schema, focused tests, and serial
  LC1-LC4/T1/T2/T3.1-T3.4 regression gate pass;
- protected-master cleanliness is observed before, during, and after the worker
  lane; the worker may not commit, push, integrate, or certify its own work;
- a fresh Gemini 3.5 Flash review returns `DECISION: pass` on the exact recovered
  head before Sol accepts, commits, and pushes.

## Authorized implementation surface

- `app/services/bernie/scenario_spec.py`
- `app/services/bernie/scale_corpus.py`
- `app/services/bernie/composed_corpus_evaluator.py`
- a new LC4R10 development-only report/check helper under `scripts/`
- a new focused LC4R10 test module under `tests/`
- source-generated development fixture groups and manifest only
- new LC4R10 documentation/report/provenance artifacts

Do not edit old LC4R1-LC4R9 reports, old acceptance artifacts, protected
fixtures, or unrelated product surfaces.
