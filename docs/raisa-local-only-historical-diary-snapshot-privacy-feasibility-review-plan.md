# Raisa local-only historical Diary snapshot privacy feasibility review — plan

Date: 2026-08-24

Timestamp: 2026-08-24T01:33:35.0694120+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_plan`

Operation: `raisa-local-only-historical-diary-snapshot-privacy-feasibility-review`

Planning source HEAD: `19ef38730de399482b232bf6eca3233423d8d348`

Reasoning level: Extra High. This tranche defines the privacy control that must
mediate the first future read of a longitudinal private Diary archive. It must
preserve useful scheduling mechanics without confusing pseudonymisation,
local restriction or a successful synthetic rehearsal with proof of
anonymity.

## Decision and objective

The privacy gate is useful now and will be built before any historical Diary
snapshot is touched. This tranche will implement and test the gate entirely on
wholly authored synthetic timestamp-sequenced snapshots, then freeze an exact
non-executable contract for a later bounded local read.

The gate is intended to support a near-lossless local research projection. It
may retain relative observation timing, within-day state sequence, stable
nonsemantic entity linkage, slot time, duration, resource role, lifecycle and
short-lived corrections. It must remove or replace direct identities, contact
details, external identifiers, original filenames, exact source timestamps,
free text and identifying labels. The output remains private-derived and
locally restricted unless a later decision grants a narrower use; it is never
described as anonymous merely because these transformations passed.

This tranche does not open, list, search, sample, hash, parse or otherwise
inspect the historical Diary archive.

## Synthetic input and projection contract

Create `orchestration_harness/historical_diary_snapshot_privacy_gate.py` as a
pure, strict Pydantic module. Models are frozen, reject extra fields and use
closed vocabularies.

The authored-synthetic rehearsal represents:

1. relative synthetic day and observation offsets, with the nominal 30-second
   polling cadence and deliberately irregular gaps;
2. a stable raw record token, a person label, contact value, external record
   identifier, resource label and short note solely as invented detector
   targets;
3. scheduling fields needed for temporal mechanics: start minute, duration,
   lifecycle state and resource role; and
4. additions, removals and changes between adjacent observations.

The projection must:

- derive stable, domain-separated HMAC-SHA-256 stand-ins from an ephemeral key;
- never serialize that key or the original identity-bearing values;
- convert observation time to relative interval-censored bounds, never an
  original filename or wall-clock timestamp;
- preserve stable linkage and the exact scheduling fields above;
- map any note to a closed presence/sensitivity bucket and emit no note text;
- emit only a closed output-field allowlist; and
- label the result `synthetic_gate_rehearsal`, not de-identified evidence.

The direct-identifier and field-inventory gate must classify every admitted
input field. It rejects unknown fields, unclassified values, malformed contact
or identifier values, persisted-key requests, exact source timestamp fields,
paths/filenames and free-form output. It reports only category counts and
boolean outcomes, never matched source values.

## Adjacent differencing and utility invariants

Implement a deterministic adjacent snapshot differencer. Each transition is
bounded by the previous and current relative observation intervals and reports
only stable stand-in record IDs plus closed change kinds. Rehearsal acceptance
requires exact recovery of the authored additions, removals and changes,
stable linkage across observations, correct interval bounds and no invented
ordering inside an observation gap.

The existing aggregate-only H5 output validator, H15 approval and historical
Diary tools remain unchanged. The new gate is an additional privacy-feasibility
layer; it does not weaken or reinterpret any existing approval.

## Measured contextual-risk mechanics

Compute, without exporting source values:

- equivalence-class sizes over an explicit quasi-identifier projection;
- unique-record and unique-trajectory counts and rates;
- rare-sequence counts under an explicit minimum frequency;
- defined record-linkage and trajectory-linkage attack successes, trials and
  rates against authored auxiliary clues; and
- multi-release differencing successes, trials and rates across independently
  keyed synthetic releases.

All rates carry integer numerators and denominators. Empty denominators fail
closed. Metrics describe the supplied synthetic population only. They do not
estimate a universal probability of re-identification and do not themselves
authorise a real-data output.

## Frozen future real-access subgate

Emit a committed policy artifact under the operation Continuity directory.
It is data-free and non-executable in this tranche. A later accepted operation
may instantiate it only with ignored local runtime bindings satisfying all of
these controls:

- one explicitly nominated leaf root and one nominated dense day;
- non-recursive, read-only access to at most 80 explicitly inventoried files;
- an aggregate input-byte cap of 128 MiB and a per-file cap of 8 MiB;
- exact pre-read path, count and byte readback in ignored local evidence;
- an ignored local output root, newly created for that attempt;
- no symlink/reparse-point traversal and no path escape;
- provider, network, subprocess upload, clipboard, telemetry and model prompt
  use forbidden;
- no raw/extracted text, original identifiers, original filenames, exact
  timestamps, mapping key or mapping table in committed output;
- an ephemeral in-memory stand-in key destroyed before closeout;
- deterministic field-inventory, identifier, leakage and utility checks before
  any projection can be retained;
- contextual-risk metrics and a typed decision of `blocked`,
  `revision_required` or `locally_restricted_candidate`; and
- automatic cleanup on failure, with only aggregate non-PHI evidence eligible
  for commit.

`locally_restricted_candidate` means only that the bounded projection may be
retained in the ignored local research area for review. It grants no fixture,
provider, model, product, memory, runtime or publication eligibility. Any such
use requires its own later accepted gate.

The contract cannot contain a real path, discover a root, invoke a parser or
change the current H15 approval. Real access remains impossible until a later
plan binds an exact local root, parser, output location and cleanup proof.

## Hostile verification

Create synthetic-only fixtures and tests covering:

- strict models, closed vocabulary and extra-field rejection;
- complete field classification and rejection of unknown identity-like fields;
- person, telephone, address, Medicare-like, email, external-ID, path,
  filename, exact-timestamp and note-text detector cases;
- stable domain-separated stand-ins without source values or key material;
- note bucketing and a closed projection schema;
- correct add/remove/change differencing across regular and irregular polls;
- unchanged-state and empty-snapshot behavior;
- equivalence, uniqueness, rare-sequence, record-attack, trajectory-attack and
  multi-release metrics with exact numerators and denominators;
- zero-denominator, missing population, malformed auxiliary clue and unsafe
  policy failures;
- access-contract rejection of broad roots, recursion, more than 80 files,
  more than 128 MiB total, more than 8 MiB per file, network/provider/model
  permission, persisted mappings, executable access or real path material; and
- source scanning proving the module cannot enumerate, open or parse files and
  contains no import of a provider, product router, database or replay engine.

Focused verification reruns the existing historical Diary de-identification,
output-safety, leakage-lint and timeline-event tests unchanged.

## Acceptance

Pass requires:

1. the fresh five-source Ariadne receipt and valid in-progress latch;
2. explicit DeepSeek, Gemini and native-subagent dispositions;
3. the strict synthetic projection, differencer and risk metrics passing every
   hostile test;
4. a fail-closed, non-executable future access contract with the exact bounds
   above;
5. no historical Diary or private calibration reference access;
6. no change to existing H5/H15 controls or product/runtime surfaces;
7. a passing clockwork closeout, paired lay/technical Yuri summary and non-PHI
   Pushover notification; and
8. unchanged protected refs and preservation of every unrelated untracked
   file.

## Parallelism assessment

- **DeepSeek:** declined with negative leverage. The native harness remains
  paused pending its separate boot proof, this privacy invariant is serially
  coupled, and no silent Claude Code fallback is allowed.
- **Gemini:** not applicable with neutral leverage. The active tranche forbids
  provider, network and model execution, so no live verifier packet exists.
- **Native subagents:** declined with negative leverage. Field policy,
  projection, attacks and the access contract form one tightly coupled privacy
  boundary without an independently writable package.
- **GPT Sol:** owns the frozen policy, implementation, hostile verification,
  acceptance, clockwork publication and next-latch decision.

## Closed surfaces

Provider-free, local-only and unmounted. No historical Diary open/list/search/
sample/hash/parse; no private calibration reference resolution; no network,
provider or model prompt; no real or real-practice-derived committed fixture;
no patient, appointment, clinical or protected data; no product runtime,
route, API, client, database or configuration change; no ordinary-practice
enablement; no memory/RAG/GraphRAG; no production, deployment, release, Pages
or protected-ref movement. Local/origin `master` and `handoff/current` remain
exactly `2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve
`docs/branding/` and every unrelated untracked file. Stage explicit paths only.
