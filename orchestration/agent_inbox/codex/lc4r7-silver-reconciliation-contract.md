# LC4R7 Silver Contract-Quality Reconciliation — Sprint Contract

Date: 2026-07-15

Active Conductor, sprint planner, architecture/acceptance owner, recovery
owner, and protected integrator: GPT Sol. Planning mode is
`sol_direct_routine`. DeepSeek V4 Flash/high through Claude Code `--bare` owns
one bounded implementation/test lane. Gemini 3.5 Flash through Antigravity owns
the independent veto review. DeepSeek Pro is not a Conductor or worker.

Settings fingerprint:
`sha256:8001d1ecaa70140748ac50277d0beeb33db37ab03e80a635a5da66c90aa69db8`

## Direction-dialogue disposition

Skipped. Sol's development-only profiling produced a complete deterministic
queue contract. No external model plans, allocates, accepts, or integrates this
sprint.

## Protected evidence and authority boundary

Use only the ordinary Silver/pending LC4 development partition. Do not open,
enumerate, import, load, regenerate, evaluate, hash-check, infer from, or tune
against protected holdout v1 or any fixture, support module, seal, receipt, or
report belonging to it. Do not inspect historical diary material or transmit
patient/practice data. No provider inference, T3.5 adapter, route/API, database,
UI, deployment, memory, RAG/GraphRAG, confirmation, or write authority is
permitted.

Expected fields and source spans are audit evidence only. They must never feed
values into interpretation. A source-span field name does not override the
surface meaning of the authored dialogue. Generated fixtures remain unchanged
and Silver/pending; LC4R7 does not promote or adjudicate them.

## Frozen selection

Use the public ordinary development audit to select current
`aligned_failure` scenarios, then score their composed deterministic result at
one repeat. The selection is exactly 572 scenarios, hash
`e17eb1739c16f3de`.

Emit one queue record for each failed semantic field plus one
`replay_contract` record for each scenario whose semantic fields all pass but
whose composed replay still fails. Each record contains only:

- `scenario_id`;
- `dimension`;
- `disposition`;
- `reason_code`;
- `provenance: silver`; and
- `adjudication: pending`.

It must contain no utterance, entity name, expected/observed value, source-span
text, diary payload, tool payload, appointment delta, audit delta, prompt, or
provider field. The frozen queue has 1,436 records, hash
`6cb9e36b8d5309f4`, where the hash is SHA-256 truncated to 16 characters over
newline-joined, sorted
`scenario_id|dimension|disposition|reason_code` records.

## Deterministic dispositions

The queue may use only:

- `malformed` — a dangling `after`, `before`, `between`, or `around` operator
  has no extractable operand;
- `incomplete` — the contract expects a relation/value/entity semantic with no
  supporting surface point, bound, or source span;
- `contradictory` — explicit surface extraction or safe clarification behavior
  conflicts with the Silver contract;
- `mixed_contract_defect` — the same field combines unsupported expectation and
  surface/contract conflict;
- `planned_not_implemented` — native Diary grammar resolves `check_in`, which
  remains deliberately unimplemented and has no signed action;
- `requires_adjudication` — clarification policy expects clarification while
  the current safe interpreter does not; LC4R7 makes no correctness claim;
- `non_language_contract_mismatch` — semantic fields pass, but replay/delta
  vocabulary or integration expectations disagree; and
- `surface_supported_parser_gap` — independent surface evidence supports the
  Silver expectation and the interpreter misses it.

`requires_adjudication` is not a parser gap and must remain Silver/pending.
`non_language_contract_mismatch` is outside language-parser remediation.

## Frozen queue evidence

### Primary scenario disposition

Primary disposition uses the deterministic priority:
planned-not-implemented, surface-supported parser gap, requires adjudication,
non-language contract mismatch, mixed contract defect, contradictory,
malformed, incomplete.

| Primary disposition | Count | Hash |
|---|---:|---|
| contradictory | 62 | `d5e74c6e0544109f` |
| incomplete | 137 | `60f8b473eb85904d` |
| malformed | 48 | `9514dac1b6880d01` |
| mixed contract defect | 182 | `e148db0d28acdcd2` |
| non-language contract mismatch | 51 | `2e45f30f714568ef` |
| planned not implemented | 39 | `f706165328a3297f` |
| requires adjudication | 53 | `9496e23c6f339603` |
| surface-supported parser gap | 0 | `e3b0c44298fc1c14` |

The 39 planned scenarios are all `check_in` surfaces. Twenty-six fail
`intended_action`; thirteen already resemble `status_change` to the older
extractor but remain planned-not-implemented under the native Diary grammar.

### Dimension/disposition counts

| Dimension | Disposition | Count |
|---|---|---:|
| intended_action | planned_not_implemented | 26 |
| action_semantics | planned_not_implemented | 39 |
| action_semantics | contradictory | 78 |
| temporal_relation | malformed | 66 |
| temporal_relation | incomplete | 18 |
| temporal_relation | contradictory | 75 |
| normalized_values | malformed | 66 |
| normalized_values | incomplete | 220 |
| normalized_values | contradictory | 45 |
| normalized_values | mixed_contract_defect | 146 |
| entity_semantics | incomplete | 374 |
| entity_semantics | contradictory | 17 |
| entity_semantics | mixed_contract_defect | 58 |
| requires_clarification | planned_not_implemented | 26 |
| requires_clarification | contradictory | 78 |
| requires_clarification | requires_adjudication | 53 |
| replay_contract | non_language_contract_mismatch | 51 |

No queue record is `surface_supported_parser_gap`.

## Exit gate

LC4R7 is diagnostic. It authorizes no interpreter, replay, fixture, or
generator remediation. The deterministic language-bridge exit gate remains
`blocked_pending_adjudication_and_contract_reconciliation` because:

- 53 clarification-policy records require independent human adjudication;
- 51 semantic-pass records require non-language replay/delta contract
  reconciliation; and
- all remaining residuals are malformed, incomplete, contradictory, mixed, or
  planned-not-implemented Silver evidence.

Do not request holdout-v2/reuse approval yet. First resolve the 53/51 blockers
through later bounded development-only work. Protected holdout v1 remains
sealed and T3.5 remains deferred.

## Required implementation

Add a deterministic LC4R7 reconciliation helper with `--check`, a committed
redacted queue, an aggregate JSON report, a concise implementation note, and
focused tests. It must:

- reproduce every frozen count and hash above;
- be invariant to corpus input order;
- fail closed on corpus, selection, record, disposition, reason-code, queue,
  report, or baseline drift;
- prove the redacted queue schema and forbidden-field boundary;
- record current semantic counts `880/814/628/101/300/782`, safety
  `1152/1152`, and zero variance over 2,304 samples;
- retain `check_in` as planned-not-implemented;
- expose the blocked exit gate and zero authorized parser gaps; and
- import no protected, provider, route, database, UI, historical-diary,
  memory/RAG, or write surface.

Do not modify `semantic_extraction.py`, `development_gap_audit.py`, the composed
scorer/replay, action grammar, scenario schema, source-span validation, corpus
fixtures, generators, or any earlier report.

## Owned files

The worker may add exactly:

- `scripts/bernie_lc4r7_silver_reconciliation.py`;
- `tests/test_bernie_lc4r7_silver_reconciliation.py`;
- `docs/bernie-lc4r7-adjudication-queue.json`;
- `docs/bernie-lc4r7-silver-reconciliation-report.json`;
- `docs/bernie-lc4r7-silver-reconciliation.md`; and
- `orchestration/agent_inbox/codex/lc4r7-dw1-completion.md`.

No other file may change. The worker may create candidate commits but may not
integrate, push, deploy, or alter scope.

## Acceptance

Acceptance requires exact queue/taxonomy reproduction, zero authorized parser
gaps, the blocked exit gate, queue redaction/schema tests, report `--check`,
focused and proportional LC1-LC4R plus T1/T2/T3.1-T3.4 checks, clean diff,
and Gemini `DECISION: pass` on the exact recovered head.

Sprint engine state: continuing.

