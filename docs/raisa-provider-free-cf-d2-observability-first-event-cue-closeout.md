# Provider-free CF-D2 observability-first event and cue closeout

Date: 2026-08-13

Timestamp: 2026-08-13T16:23:03+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `e8677b54d1c339dcd14776ce8bf15e7db2980378`

Result: `raisa_provider_free_cf_d2_observability_first_event_cue_architecture_pass`

## Outcome

CF-D2 has a new, smaller architecture boundary. It no longer begins by trying
to prove four database crashes around one complicated recovery anchor. It first
defines the durable fact the product actually needs: a payload-free obligation
that says a practice-scoped Diary projection may be stale through a particular
source position and must be freshly read.

Source truth, event observation, classification, cue obligation, checkpoint,
delivery, Reception One reconciliation and command execution now have disjoint
authority. A checkpoint may advance only through contiguous positions with one
terminal classification receipt and any required cue obligation created
atomically. Delivery may lag behind as an independently visible backlog.

The cue contains no appointment or person identifier, status, time or event
payload. It cannot update the screen directly or prove a command succeeded.
Reception One must perform a fresh practice/role/resource-scoped read, and any
later consequential command must still recheck current authority and source
truth inside its transaction.

## Observability gained

Ten operational conditions now have ten distinct payload-free observations and
safe responses: unknown source head, observation lag, position gap,
classification gap, classification rejection, obligation gap, dispatch lag,
dispatch failure, fenced ownership and reconciliation failure. Unknown or
epoch-mismatched lag cannot be reported as zero.

This directly applies the accepted CF-D2 workflow repair. A future diagnosis
must distinguish every remaining hypothesis before it spends a correction or
runtime attempt. The old generic `unexpected_terminal_success` shape is not an
admitted diagnostic coordinate in this architecture.

## Verification

- the closed JSON schema and semantic validator admit the canonical contract;
- all 39 independent hostile mutations fail closed;
- all ten diagnostic stages retain unique observations and safe responses;
- the non-invasive API Spine artifact keeps runtime and route changes blocked;
- 114 focused event/API Spine/source-truth/latch tests pass;
- Ruff and formatting pass;
- the canonical fast profile passes 193 tests, compilation of 209 maintained
  Python sources, Diary JavaScript syntax and Git whitespace; and
- exact source and origin task branch are published at
  `e8677b54d1c339dcd14776ce8bf15e7db2980378` with protected refs unchanged.

No external worker or provider was selected. The tightly coupled architecture
and deterministic evidence remained Sol-owned under the worker-economy rule.

## Preserved evidence and limits

CF-D1 remains accepted concurrency evidence. Both original CF-D2 stops and the
stopped recovery descendant remain immutable negative evidence. This result is
not a retry or promotion of their four-crash anchor protocol.

The tranche proves architecture only. It does not prove a watcher, database
representation, persistence, transaction, crash/restart, unknown commit,
delivery, latency, retention, rotation, application wiring, product-data safety,
deployment or production.

## Next tranche

The next dependency-satisfied tranche is the provider-free unmounted event/cue
admission rehearsal. It will exercise pure authored-synthetic sequences for
terminal classification, duplicates, position gaps, checkpoint eligibility,
coalescing, fencing and fresh-read reconciliation results against this exact
contract. It opens no watcher, database/source, persistence, provider, route or
command.

Protected evidence, historical Diary/PHI, patient/product/clinical data,
external patient clients, real identity, operational retention, provider/ADC,
credentials/IAM/network, executable tools, commands/writes, deployment,
production, release, Pages and protected refs remain closed. `docs/branding/`
and all unrelated untracked files remain preserved and excluded.
