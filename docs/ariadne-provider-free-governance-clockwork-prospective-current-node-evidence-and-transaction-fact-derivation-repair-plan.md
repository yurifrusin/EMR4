# Provider-free governance clockwork prospective current-node evidence and transaction-fact derivation repair — plan

Date: 2026-08-23

Timestamp: 2026-08-23T16:18:40.5972422+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`ariadne-provider-free-governance-clockwork-prospective-current-node-evidence-and-transaction-fact-derivation-repair`

## Purpose

Remove the three postpublication rollback sequences measured in the preceding
closeout by extending the existing clockwork preparation pass. The repaired
tick will validate the complete prospective current-node human-evidence set
before pointer movement and will emit its own invocation, lease, generation,
publication and rollback facts.

This is an operator-interface repair. It does not relax a safety invariant or
create a second workflow system.

## Exact implementation surface

Only these existing implementation and test files may change:

- `orchestration_harness/governance_clockwork_tick.py`;
- `scripts/ariadne_governance_clockwork_tick.py`;
- `tests/test_ariadne_governance_clockwork_tick.py`; and
- `tests/test_current_baton_consistency.py`.

Normal tranche plan, threat, evidence, closeout, acceptance and Yuri-summary
records remain permitted. No new required operator input, approval, named gate,
runtime control layer, schema field or closeout document is permitted.

## Prospective human-evidence contract

Before `transactional_closeout.prepare_transaction` and before any canonical
write, every clean-closeout tick will inspect the prospective node's `plans`,
`closeouts` and `acceptances` evidence categories in that deterministic order.
One preparation pass will return the complete ordered set of all detectable
errors for those categories.

The pass must check:

1. each category is a non-empty list;
2. each entry is a unique safe repository-relative Markdown path outside
   `docs/branding/`;
3. each path exists as a file;
4. the first twelve lines contain exactly one top-level `Date:` and one
   top-level `Timestamp:`;
5. `Date:` is ISO calendar form;
6. `Timestamp:` is ISO, explicitly offset, names `Australia/Brisbane`, uses
   the Brisbane `+10:00` offset, and has the same calendar date; and
7. all errors are returned together under one closed
   `tick_prospective_current_node_evidence` rejection.

The repository consistency test will consume the same production header
validator. The model or operator must not reconstruct a second timestamp
parser.

## Machine-owned transaction facts

The CLI will add one output-only `transaction_facts` reading. It will derive,
without intent fields:

- invocation, preparation, publication and rollback attempt counts for the
  current command;
- published-generation and byte-exact-rollback counts for the current command;
- idempotent readback disposition;
- base, target and advance lease readings; and
- prepared, previous and selected generation identifiers.

The existing compatibility fields remain, but their values must be derived
from this reading. A dry check reports one preparation and zero publication;
a clean publication reports one preparation and one publication; an exact
published-intent readback reports no new preparation or publication; and a
rollback reports one rollback and one byte-exact restoration.

These are invocation facts, not a manually reconstructed historical total.
Later efficacy aggregation may consume exact retained outputs, but this tranche
adds no ledger or operator counter.

## Frozen hostile fixtures

Focused tests must prove:

- at least two different prospective Markdown files can each contain multiple
  timestamp defects and every defect is returned in one ordered rejection;
- duplicate, unsafe, non-Markdown, missing-file and malformed category entries
  are accumulated rather than stopped at the first defect;
- a valid complete prospective evidence set still builds the byte-identical
  semantic projections expected by the existing clockwork tests;
- dry, publish, idempotent readback and rollback outputs expose exact generated
  transaction facts; and
- all existing pre-pointer restoration, pointer-last commit, stale-predecessor,
  single-writer, digest, protected-ref and byte-exact rollback tests remain
  unchanged and pass.

## Acceptance and efficacy

The tranche passes only if:

1. the complete prospective error set is available before any live write;
2. the current two missing-timestamp failure shapes and the manually authored
   publication-counter shape are no longer possible through the normal CLI;
3. zero new required operator fields, approvals, gates or closeout documents
   are added;
4. all focused and surrounding governance tests pass before the repaired live
   publication path is used;
5. existing single-writer, full-Git binding, closed vocabularies,
   protected-boundary floor, pointer-last publication and byte-exact rollback
   remain intact; and
6. protected refs remain exactly
   `2e34bdad732fdab32fbf778280b3d3c70d66d602`, with `docs/branding/` and every
   unrelated untracked file preserved.

The matched efficacy reading will record operator-input fields added, errors
returned per preparation, publication attempts, rollbacks and accepted repair
yield. Elapsed time remains a bounded proxy only.

## Parallelism assessment

- **DeepSeek:** declined. The native occupied profile is paused, Claude Code is
  not a fallback, provider work is closed and the repair is tightly coupled to
  the single canonical writer and rollback state.
- **Gemini:** declined. This is a provider-free deterministic control repair;
  no model call is authorised.
- **Native subagents:** declined under current developer policy and because
  implementation, fixtures, pointer safety and acceptance are serially
  coupled.
- **Owner:** GPT Sol.

Reassess only if the exact existing-tick boundary cannot contain the repair or
if implementation would require a new field, gate, document or control layer.
