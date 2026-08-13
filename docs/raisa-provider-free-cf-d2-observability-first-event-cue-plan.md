# Provider-free CF-D2 observability-first event and cue plan

Date: 2026-08-13

Timestamp: 2026-08-13T16:04:58+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_unmounted_architecture_execution`

Planning baseline: `6f8904c5f7c8ab268c2010bd2c4f859d998ff1a4`

Target result: `raisa_provider_free_cf_d2_observability_first_event_cue_architecture_pass`

## Objective

Define the smallest restart-safe event and cue delivery contract worth proving
for Reception One now that its visible staff status consumer exists. The cue
must only say that a practice-scoped Diary projection may need refreshing. It
must never duplicate appointment truth, prove command success, confer authority
or remove the command service's current-truth recheck.

This is the fresh observability-first return permitted by the accepted
source-owned-truth reorientation. It retains CF-D1 as concurrency evidence and
the two stopped CF-D2 sequences as immutable negative evidence. It is not a
retry of their four-crash anchor protocol.

## Boundary classification

- API Spine class: non-invasive async/event architecture contract.
- Data: newly authored synthetic, patient-free coordinates and digests only.
- Runtime: none.
- Evidence: repository-local deterministic contract validation only.
- Authority: events are acceleration hints; REST/OpenAPI commands remain the
  sole mutation plane; fresh authorised reads remain the display plane.

## Frozen minimal contract

1. One partition is an exact source-system, practice-scope-digest and event-
   family tuple. One logical consumer owns each partition; future active/
   standby replicas require an external lease and fencing generation.
2. A position is an opaque source epoch plus a positive monotone integer. The
   source head, observed position and durable checkpoint are distinct.
3. Every observed position receives one immutable terminal classification
   receipt: `cue_required`, `suppressed_irrelevant` or
   `rejected_unsupported`. A rejection never becomes a cue.
4. A checkpoint is the highest contiguous position whose terminal receipt is
   durable and whose required cue obligation was created atomically with that
   receipt. Delivery and user-session fan-out are not checkpoint prerequisites.
5. A cue obligation contains only practice scope, consumer scope, event family,
   a contiguous position range, one allowlisted reason code and
   `fresh_authorized_read_required: true`. It carries no appointment state,
   person identifier, free text, command evidence or confirmation evidence.
6. Duplicate observation reuses the same receipt and obligation. Out-of-order
   observation may be recorded, but the checkpoint cannot cross a gap.
   Contiguous pending obligations for the same consumer and reason may coalesce
   without changing their lower and upper source positions.
7. Delivery is at least once. Duplicate, late or missing cues affect refresh
   latency only. The consumer deduplicates by obligation identity, performs a
   fresh scoped read and reconciles authoritative projection truth.
8. Operator evidence is payload-free and stage-specific. It distinguishes
   source-head unknown, observation lag, position gap, classification gap or
   rejection, obligation gap, dispatch lag or failure, ownership fencing and
   reconciliation failure. No generic coordinate may collapse those stages.

## Owned artifacts

- this plan;
- `docs/raisa-provider-free-cf-d2-observability-first-event-cue-architecture.md`;
- `docs/security/raisa-provider-free-cf-d2-observability-first-event-cue-threat-model-delta.md`;
- `docs/api-spine/async/durable-diary-event-cue-observability.yaml`;
- the closed JSON contract and schema under
  `orchestration/continuity/raisa-provider-free-cf-d2-observability-first-event-cue/`;
- one pure acceptance script and focused tests; and
- exact acceptance, closeout, Yuri mailbox and continuity artifacts if the
  deterministic gate passes.

## Acceptance

- The closed schema and semantic validator admit the canonical contract.
- Cue, event, source truth, Context Frame and command authority remain
  disjoint.
- Checkpoint advancement requires contiguous terminal classification and
  atomic required-obligation creation, but never delivery.
- Duplicate, out-of-order, missing and rejected observations have exact
  fail-closed outcomes.
- Lag is typed as exact, unknown or epoch-mismatch; unknown is never zero.
- The complete failure-stage census has mutually distinct operator evidence
  and a one-to-one discriminating diagnosis.
- The visible Diary consumer always performs a fresh authorised read; a cue
  payload cannot supply the displayed status or authorize a command.
- At least 24 hostile mutations fail closed.
- API Spine artifact tests, focused tests, canonical fast verification and Git
  whitespace pass.

## Recovery and next descendant

Deterministic failures are repaired inside this one frozen boundary. No
external review is required unless a hard authority ambiguity or substantive
security finding emerges. No database or Docker contact is eligible in this
tranche.

After acceptance, the next dependency-satisfied descendant is a provider-free,
unmounted admission rehearsal over authored-synthetic observation sequences.
It may exercise pure state transitions for duplicates, gaps, coalescing,
fencing and reconciliation results. It may not start a watcher, open a source
or database, persist operational state, call a provider, issue a command or
change a route.

## Closed surfaces

No watcher/listener/worker, database/source, migration, operational retention,
product/patient/clinical data, external patient client, real identity,
provider/ADC, credential/IAM/network, executable tool, command/write,
GraphQL/OpenAPI route change, deployment, production, release, Pages or
protected-ref movement is authorised. `docs/branding/` and every unrelated
untracked file remain preserved and excluded; staging is explicit-path only.
