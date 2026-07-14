# LC4R8 Exit-Blocker Reconciliation — Sprint Contract

Date: 2026-07-15

Active Conductor, sprint planner, architecture/acceptance owner, recovery
owner, and protected integrator: GPT Sol. Planning mode is
`sol_direct_routine`. DeepSeek V4 Flash/high through Claude Code `--bare` owns
one bounded implementation/test lane. Gemini 3.5 Flash/medium through a fresh
Antigravity project owns the independent veto. DeepSeek Pro is not a Conductor
or worker.

Settings fingerprint:
`sha256:8001d1ecaa70140748ac50277d0beeb33db37ab03e80a635a5da66c90aa69db8`

## Direction-dialogue disposition

Skipped. Sol's development-only profiling produced a complete deterministic
contract. No external model plans, allocates, accepts, or integrates this
sprint.

## Protected evidence and authority boundary

Use only the ordinary Silver/pending development partition and accepted LC4R7
redacted queue. Do not open, enumerate, import, load, regenerate, evaluate,
hash-check, infer from, or tune against protected holdout v1 or any fixture,
support module, seal, receipt, or report belonging to it. Do not inspect
historical diary material or transmit patient/practice data. No provider
inference, T3.5 adapter, route/API, database, UI, deployment, memory,
RAG/GraphRAG, confirmation, or write authority is permitted.

Expected contract fields are audit evidence only. They must not feed values
into interpretation. LC4R8 does not modify runtime interpretation, the core
scorer/replay, corpus generators, or generated fixtures.

## Clarification decision surface

The accepted LC4R7 `requires_adjudication` selection is exactly 53 scenarios,
hash `9496e23c6f339603`. For each scenario, recompute the deterministic composed
result and examine semantic failures other than `requires_clarification`.

Every scenario has at least one upstream semantic contract failure. The
decision surface is therefore not yet policy-decision-ready:

| Blocker class | Count | Scenario hash |
|---|---:|---|
| `normalization_contract_blocked` | 3 | `db484a50adc0b601` |
| `entity_and_normalization_contract_blocked` | 6 | `ff20612b3c9e276e` |
| `temporal_and_normalization_contract_blocked` | 20 | `910950860133d8b9` |
| `temporal_entity_and_normalization_contract_blocked` | 24 | `7cfaa6e4ddefc172` |
| `isolated_clarification_policy_choice` | 0 | `e3b0c44298fc1c14` |

The action distribution is create 13 (`1839c8c567e44922`), move 13
(`ec7e009f37f0834a`), resize 14 (`e49785ce6f8922e5`), and cancel 13
(`830386f883de7fd0`). This distribution is context only and does not authorize
action-specific policy.

Emit 53 redacted records with exactly:

- `scenario_id`;
- `blocker_class`;
- `decision_readiness: blocked_by_upstream_contract_defect`;
- `provenance: silver`; and
- `adjudication: pending`.

Their record hash is `baf4c66b1a7ee139`, computed as truncated SHA-256 over
sorted newline-joined `scenario_id|blocker_class|decision_readiness` lines.
Zero records are decision-ready. LC4R8 must not silently choose whether Bernie
should clarify.

## Replay/delta contract audit

The accepted LC4R7 `non_language_contract_mismatch` selection is exactly 51
scenarios, hash `2e45f30f714568ef`. Recompute deterministic interpretation,
replay, and composed component results. Apply this priority order:

1. `negated_surface_conflicts_with_create_contract` when the interpreter marks
   the action negated but the Silver contract still expects creation;
2. `clarification_tool_without_clarification_contract` when the expected tool
   sequence is only `request_clarification` while the contract has no expected
   clarification;
3. `audit_change_type_vocabulary_only` when outcome, both tool comparisons,
   authority, clarification, and appointment deltas all pass and only the
   audit delta fails;
4. `creation_expectation_conflicts_with_replay_policy` when the contract
   expects `appointment_created`, replay correctly yields no outcome, and the
   expected and replay tool sequences agree; and
5. `genuine_replay_integration_defect` for any remainder.

The frozen result is:

| Blocker class | Count | Scenario hash |
|---|---:|---|
| `audit_change_type_vocabulary_only` | 11 | `b88018991e49ffd5` |
| `clarification_tool_without_clarification_contract` | 11 | `dc7446b93a05c648` |
| `creation_expectation_conflicts_with_replay_policy` | 28 | `3206003d4bc39a23` |
| `negated_surface_conflicts_with_create_contract` | 1 | `020fade8ca644684` |
| `genuine_replay_integration_defect` | 0 | `e3b0c44298fc1c14` |

Emit 51 redacted records with exactly:

- `scenario_id`;
- `blocker_class`;
- `remediation_status`;
- `provenance: silver`; and
- `adjudication: pending`.

Only `audit_change_type_vocabulary_only` receives
`authorized_for_generator_backed_contract_repair`; every other class receives
`not_authorized_contract_reconciliation_required`. Their record hash is
`2fabb972ad0bc00b`. The combined clarification/replay record hash, with
`clarification|` or `replay|` prefixed to each canonical line, is
`fd0de59a2967ddf8`.

Authorization is diagnostic only in LC4R8. Do not change the comparator to
treat `create_requested` and `created` as universally equivalent, edit
generated fixtures in place, regenerate the corpus, or change replay policy.
The 11-case repair requires a later generator-backed contract sprint with its
own frozen delta.

## Exit decision

LC4R8 must report:

- clarification policy decision-ready count: 0;
- genuine replay integration defect count: 0;
- generator-backed contract repair authorized count: 11;
- upstream clarification contract blockers: 53;
- remaining replay contract reconciliation blockers: 40; and
- exit status: `blocked_pending_generator_repair_and_contract_reconciliation`.

Do not request holdout-v2/reuse approval yet. The next ordinary tranche may
implement only the frozen 11-case generator-backed audit-vocabulary repair or
further reconcile the upstream Silver contracts. A material clarification
policy choice remains a user decision boundary only after isolated,
decision-ready cases exist.

## Required implementation

Add a deterministic LC4R8 helper with `--check`, two redacted record artifacts,
an aggregate report, a concise implementation note, and focused tests. It must:

- reproduce every frozen count and hash above;
- be invariant to original, deterministic-shuffled, and reversed development
  input order using a real explicit-variant entry point;
- fail closed on corpus, LC4R7 selection, record schema/value, unexpected
  class, count/hash, report, baseline, safety, variance, or exit drift;
- validate committed artifacts against contract constants rather than deriving
  expected values from observed output;
- preserve semantic counts `880/814/628/101/300/782`, safety `1152/1152`, and
  zero variance over 2,304 samples;
- expose zero policy-ready clarification cases and zero genuine replay defects;
  and
- import no protected, provider, route, database, UI, historical-diary,
  memory/RAG, or write surface.

Do not modify the LC4R7 helper or artifacts, `semantic_extraction.py`,
`development_gap_audit.py`, the composed scorer/replay, action grammar,
scenario schema, source-span validation, corpus fixtures, generators, or any
earlier report.

## Owned files

The worker may add exactly:

- `scripts/bernie_lc4r8_exit_blocker_reconciliation.py`;
- `tests/test_bernie_lc4r8_exit_blocker_reconciliation.py`;
- `docs/bernie-lc4r8-clarification-decision-surface.json`;
- `docs/bernie-lc4r8-replay-contract-audit.json`;
- `docs/bernie-lc4r8-exit-blocker-report.json`;
- `docs/bernie-lc4r8-exit-blocker-reconciliation.md`; and
- `orchestration/agent_inbox/codex/lc4r8-dw1-completion.md`.

Acceptance requires exact taxonomy reproduction, real order invariance,
fail-closed checks, artifact redaction, clean diff, focused and proportional
LC1-LC4R8 plus T1/T2/T3.1-T3.4 checks, and Gemini `DECISION: pass` on the exact
recovered source head.

Sprint engine state: continuing.
