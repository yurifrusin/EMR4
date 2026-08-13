# Provider-free disposable PostgreSQL CF-D2 event and cue behavior/transaction rehearsal closeout

Date: 2026-08-13

Timestamp: 2026-08-13T20:54:23+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `f4bd8ca5ec0654f8be7b1d2d74b1aca444038ee9`

Result: `raisa_provider_free_disposable_postgresql_cf_d2_event_cue_behavior_transaction_pass`

## Outcome

One newly owned networkless, portless, tmpfs-backed PostgreSQL 16 server
executed the exact accepted 12,022-byte CF-D2 artifact and six fixed serial
authored-synthetic scenario groups. All five accepted transaction protocols
passed:

- terminal admission fences the current generation, reuses an exact duplicate,
  rejects divergent identity and binds required receipt/obligation effects in
  one transaction;
- pending coalescing extends only an adjacent identical-scope/reason range and
  never mutates a delivered obligation;
- checkpointing advances only over a contiguous terminal sequence with required
  obligation coverage and correctly does not wait for delivery;
- dispatch records monotone attempts, preserves a stable failure class, leaves
  failures pending and commits delivery with the attempt; and
- reconciliation requires a delivered attempt, enforces the six-outcome truth
  table, reuses an exact duplicate and refuses a conflicting second result.

Three deliberately induced post-write failures restored byte-equivalent
canonical state digests. Eleven hostile protocol transitions left state
unchanged. All five protocols exposed their required uncontended
`RowShareLock` relation subsets. The exact captured container was reverified,
removed and proven absent.

## Issues found and resolved

The first command-line launch stopped before Docker because the new harness
used a package-form sibling import that pytest could resolve but direct file
execution could not. The bounded repair supports both package and direct script
entry points. Focused tests passed before the fresh occupied database attempt;
there was no container, SQL execution or database result in the failed launch.

The broader regression then found three stale lifecycle assertions: two still
required the historical pre-parse pause, and one still fixed Compass to the
inert-DDL node. The repair preserves those historical facts in their journey
node while mechanically validating the current latch and current advancing
Compass position. No product or protocol behavior changed.

## Verification

- nine exact source bindings and the exact artifact identity passed;
- all 64 hostile closed-contract mutations failed admission;
- all six groups, five protocols, three rollback probes, eleven denied
  transitions and five lock-footprint observations passed;
- 215 CF-D2, API Spine, latch, baton and Compass tests pass serially;
- the canonical fast profile passes Ruff, compilation of 209 maintained Python
  sources, 193 API Spine/handover/receipt/maintenance tests, Diary JavaScript
  syntax and Git whitespace; and
- exact source `f4bd8ca5ec0654f8be7b1d2d74b1aca444038ee9` is published on the task
  branch while local/origin `master` and `handoff/current` remain exactly
  protected `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

No subagent, external worker, independent verifier or provider was selected.
Sol owned the tightly coupled serial database execution and source-bound review
under the worker-economy rule.

## Claim boundary

This proves only the fixed single-server serial effects, refusals, rollback and
uncontended lock footprints of the five accepted protocols using authored-
synthetic rows in a destroyed server. It does not prove multi-session
concurrency, contention behavior, restart/crash/unknown commit, source
observation, real delivery, operational persistence/retention, real authority
or fresh reads, application wiring, migration safety, deployment or production.

Events and cues remain acceleration hints. A future consumer must still make a
fresh authorised source read, and every consequential command must still
recheck current authority and source truth inside its own mutation transaction.

## Place in the programme and next work

This closes the narrow serial database foundation that CF-D2 was trying to
establish. The durability mechanism now has an honest, bounded proof of its
payload-free refresh-obligation bookkeeping without becoming the correctness
kernel or delaying commands on event delivery.

The next dependency-satisfied tranche is a fresh read-only Compass/baton
orientation after CF-D2. Its purpose is to select the next already-planned
Reception One/product direction from repository evidence, not to open a
watcher, runtime or product change by itself. Yuri's attention is not required
for the orientation.

Concurrency, restart/unknown commit, watcher/source access, operational
persistence/retention, external patient channels, product/patient data,
provider/ADC, credentials/IAM/network, product command/write, deployment,
production, release, Pages and protected refs remain closed.
