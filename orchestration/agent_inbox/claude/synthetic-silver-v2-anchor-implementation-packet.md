# Synthetic Silver V2 Dialogue-Free Anchor Implementation Packet

Date: 2026-07-17

## Assignment

Implement the bounded dialogue-free v2 anchor builder, fail-closed coherence
validator, deterministic fixture writer/checker, and focused tests from the
already frozen and independently accepted Sol contract. Do not author v2
candidate dialogue and do not reinterpret the contract taxonomy.

## Workspace, source, and ownership

- worktree: `C:\Users\sarashera\EMR4-worktrees\synthetic-silver-v2-anchor-worker`
- branch: `codex/worker-synthetic-silver-v2-anchors`
- source branch: `codex/synthetic-silver-v2`
- exact source head: `1be60774`
- implementation worker: DeepSeek V4 Flash/high through Claude Code `--bare`

Owned files only:

- `app/services/bernie/synthetic_noise_v2.py`
- `scripts/bernie_synthetic_silver_v2_anchors.py`
- `tests/test_bernie_synthetic_silver_v2_anchors.py`
- `tests/fixtures/bernie_synthetic_noise/semantic_seeds_v2.json`
- `orchestration/agent_inbox/claude/synthetic-silver-v2-anchor-worker.md`

Do not modify any other file. Commit the owned files on the worker branch; do
not push any ref. You have no candidate-generation, admission, parser-repair,
acceptance, integration, handoff, or protected-ref authority.

## Authoritative inputs

- `docs/bernie-synthetic-silver-v2-anchor-contract.md`
- `orchestration/agent_inbox/antigravity/synthetic-silver-v2-precontent-review.md`
- ordinary development loader and scenario schema only:
  `app/services/bernie/scale_corpus.py`,
  `app/services/bernie/scenario_spec.py`, and
  `app/services/bernie/corpus_tier.py`
- v1 implementation patterns only, not v1 oracle meaning:
  `app/services/bernie/synthetic_noise_corpus.py`

Protected V1-V10 fixtures/supports/manifests/seals/receipts/reports, historical
diary data, appointment-call data, and external corpora are forbidden. Do not
run broad discovery commands. V1 synthetic fixture files are immutable and
must not be modified.

## Required implementation

Create a new v2 module without changing v1 constants or behavior.

1. Define v2 seed and manifest schema constants, a 96-anchor count, the exact
   six-action and eight-form orders, a default v2 fixture path, canonical JSON,
   SHA-256 hashing, builder, validator, writer, and checker.
2. Load only `DevelopmentOnlyLoader().load_all()`. Select deterministic named
   ordinary-development source scenarios as provenance bases. Bind every
   source with `compute_scenario_hash`; never export source dialogue,
   descriptions, or source spans.
3. Build exactly two anchors for each action/form cell. Each action must have
   16 anchors; each form 12. Source selection must be deterministic, must use
   an action-matching ordinary scenario, and must supply complete fictional
   reference/date/diary/entity and action-specific delta shapes.
4. Store a complete dialogue-free `semantic_contract`, including reference
   date, clinic clock, action and entity semantics, temporal bounds and
   normalized values, duration, diary/entity state, initial diary state,
   outcome, tools, appointment/audit deltas, forbidden outcomes/tools,
   clarification question/choices, and explicit `action_withdrawn` boolean.
5. Store a `dialogue_form_contract` with the exact local surface requirements
   for the anchor's form. Store deterministic `required_evidence_keys`, an
   authority-all-false object, source bindings, cell variant, and seed hash.
6. The manifest must say `contains_source_utterances=false`,
   `protected_holdout_access=false`, `historical_diary_access=false`, and
   `external_corpus_access=false`.

## Required coherence construction

- Standard successful mutation: action-specific mutation tools, successful
  action-specific outcome, and matching non-empty appointment/audit deltas.
- Schedule explanation: read tools, `schedule_explained`, no deltas.
- Clarification: cell variant 1 is explicit patient ambiguity and variant 2 is
  explicit practitioner ambiguity; non-null question, at least two fictional
  choices, sole tool `request_clarification`, outcome
  `clarification_required`, no deltas, `action_withdrawn=false`.
- Reversal: final whole action withdrawn; intended action remains in the
  semantic contract, `action_withdrawn=true`, null outcome, no deltas, and only
  `search_patients` when a patient is part of the action or an empty tool list
  for schedule explanation. It is not clarification.
- Correction: explicitly requires replacement of practitioner or temporal
  value and freezes final corrected semantics; it remains a successful action.
- Ellipsis/anaphora/repetition/session restart: require local recoverability,
  one final action, and successful action-specific policy/replay contracts.

The validator must independently reject every contradiction class above. It
must not call the product interpreter or scorer.

## Tests and exact checks

Focused tests must cover:

- exact 96/192 target math, action/form/cell balance, unique IDs and hashes;
- deterministic regeneration equal to the committed fixture;
- no dialogue/source spans/descriptions in anchors;
- exact source action/hash binding without protected access;
- all authority and access fields false;
- mutation, schedule-read, clarification, and reversal invariants;
- at least one mutation test per contradiction class demonstrating validator
  rejection after tampering;
- correction and local-recovery form contracts; and
- no import of product interpreter, replay, or scorer modules.

Run serially with the integration environment:

```text
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_synthetic_silver_v2_anchors.py --write
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_synthetic_silver_v2_anchors.py --check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_bernie_synthetic_silver_v2_anchors.py tests\test_bernie_synthetic_noise_corpus.py
git diff --check
```

## Durable worker report

Record implementation details, actual tests, exact fixture/manifest hashes,
any deviation, and protected access in the owned worker report. End it with:

```text
DECISION: candidate_ready|revision_required
SOURCE_HEAD: 1be60774
ANCHORS: <n>/96
ACTION_BALANCE: <n_each>
FORM_BALANCE: <n_each>
COHERENCE_ERRORS: <n>
TESTS: <passed>/<selected>
PROTECTED_ACCESS: false
```

If the frozen contract cannot be implemented mechanically, return
`revision_required` without inventing taxonomy or changing another file.
