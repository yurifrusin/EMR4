# Bernie LC4R10 Contract Reconciliation

## Outcome

LC4R10 closes the frozen development-only 53 clarification and 40 replay
contract populations. All 93 records now pass the complete deterministic
interpretation/replay/scorer contract without parser remediation.

The 53 apparent clarification cases were resolved two-turn dialogues: their
second turn already supplied the missing detail. Their temporal,
normalization, entity, duration, clarification, tool, outcome, and delta
contracts now come from the four authored create/move/resize/cancel templates.
They are not copied from interpreter or scorer expectations.

The 40 replay cases divide into:

- one withdrawn reversal with explicit null outcome, search-only tools, and no
  deltas;
- one corrected overlap with candidate selection, create-path tools, and no
  deltas;
- 14 valid create-policy alignments for same-day-distinct or terminal prior
  appointment state; and
- 24 fail-closed records with explicit null outcomes and no deltas.

`expected_outcome_kind` is now required but nullable. Omission remains invalid;
explicit JSON null records deterministic absence rather than missing evidence.

## Frozen selections

| Population | Count | Hash |
|---|---:|---|
| Resolved clarification | 53 | `9496e23c6f339603` |
| Replay reconciliation | 40 | `defe4c59877753e9` |
| Combined, disjoint | 93 | `d8d138cb267b4304` |

The post-policy resolved-dialogue outcome split is 22 action outcomes
(`e9b8e74b01d3ffc6`) and 31 fail-closed outcomes
(`73229d3e6f4a355c`).

## Verification

- corrected contract: 93/93 complete passes;
- full semantic counts: `880/814/672/154/330/835` over 1,152 scenarios;
- safety: 1,152/1,152;
- deterministic variance: zero over 2,304 samples;
- focused Sol recovery tests: 20/20;
- `scripts/bernie_lc4r10_contract_reconciliation.py --check`: pass;
- full regeneration: byte-for-byte identical;
- only the 53 source-selected group files and manifest changed;
- no parser/extraction behavior changed.

The repeat evaluator also now preserves `action_negated` when assigning sample
indexes. Without that lossless field copy, the withdrawn reversal was replayed
as a simulated write in the aggregate report; LC4R10 converts that discovered
integration defect into a permanent regression test.

## Worker and recovery provenance

DeepSeek V4 Flash/high ran once through Claude Code `--bare`. Sol rejected its
self-certified pass because its artifact disclosed only 22/93 complete passes
and 37/93 outcome matches. The candidate also broadened resolved-dialogue
overrides to every `mt_*_01` and rewrote all 96 groups. No Flash correction loop
was opened. Sol used the recovery lease and independently produced the accepted
source, report, and tests. The preserved evidence is in
`orchestration/agent_inbox/codex/lc4r10-dw1-completion.md` and
`orchestration/agent_inbox/codex/lc4r10-sol-recovery-amendment.md`.

## Boundaries

Protected holdout v1 was not opened, enumerated, imported, loaded, regenerated,
evaluated, hash-checked, inferred from, or reused. Historical diary material was
not inspected. No provider inference, route/API, database, UI, deployment,
release, memory, RAG/GraphRAG, confirmation, or live/write authority was used.
T3.1-T3.4 remain intact and blocked by default; T3.5 remains deferred.

The machine-readable authority artifact is `docs/bernie-lc4r10-report.json`.
