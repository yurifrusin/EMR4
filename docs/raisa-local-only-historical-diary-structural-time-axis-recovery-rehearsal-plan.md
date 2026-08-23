# Raisa local-only historical Diary structural time-axis recovery rehearsal — plan

Date: 2026-08-24

Timestamp: 2026-08-24T04:21:32.7833986+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_plan`

Operation: `raisa-local-only-historical-diary-structural-time-axis-recovery-rehearsal`

Planning source HEAD: `4f559aa04ebb997bc92b6f1a5a0ca26231ed9bf3`

Reasoning level: Extra High. This tranche interprets private historical Diary
structure and decides when the first downstream-use gate becomes useful. It
must recover scheduling time without guessing from a clinic opening hour,
exposing source content or quietly turning local measurement into scenario
authority.

## Decision and objective

Recover a trustworthy time-of-day mapping from the already extracted Word
table-cell text by recognising the document's paragraph sequence inside each
cell. The predecessor treated an entire multi-paragraph cell as one value;
committed H3/H4 count-only evidence shows that the documents instead contain
78 time-like tokens, 37 unique time-like tokens and a 10-minute interval mode
while retaining a stable `1x11+1x3` table shape. The recovery may use those
known structural facts, but it may not read or display a source value while
designing or testing the mapper.

The first-use gate is useful now because a successful result could make a
historical-derived scenario the next dependency-satisfied operation. This
tranche therefore freezes
`historical-derived-scenario-first-use-gate.json`. The gate is default-deny and
must be evaluated before any reusable fixture, scenario, corpus item, replay,
memory object or product test is materialised from the historical projection.
It does not burden wholly authored-synthetic tests or the private local
measurement itself, and this tranche cannot open it.

## Closed structural mapper

The mapper must:

1. split each private Word table cell on Word paragraph/manual-line boundaries,
   preserving empty positions and a bounded zero-based segment ordinal;
2. recognise only a complete closed `H:MM`, `HH:MM`, `H.MM` or `HH.MM` token,
   with an optional AM/PM suffix, as an explicit time anchor;
3. map a non-empty, non-date segment only to the nearest preceding explicit
   anchor in the same original table cell;
4. never infer a time from table row, column, segment number, file timestamp,
   assumed opening hour, a neighbouring cell or a majority guess;
5. reject an anchor sequence that moves backwards, while allowing a repeated
   time for a structural double booking;
6. require at least three distinct mapped minutes and a deterministic positive
   interval mode before the result can be a local candidate;
7. retain unmapped pre-anchor and nonconforming segments as contained
   structural occupancy with `time_minute=null`, not silently discard them;
8. include the segment ordinal in position/diff identity so several entries in
   one legacy table cell cannot overwrite one another; and
9. expose only aggregate anchor, interval, mapped/unmapped and rejection counts.

The mapper may label records only as structural occupancy segments. It may not
infer patient, appointment, check-in, cancellation, status, clinical, staff or
resource semantics.

## Synthetic-first verification

Before any new manifest or archive content access, authored-synthetic tests
must prove:

- paragraph and manual-line splitting preserves empty alignment positions and
  removes only Word end-of-cell markers;
- inline anchors map later segments and stop at the next anchor;
- headers before the first anchor remain unmapped;
- decreasing anchors fail closed and repeated anchors are allowed;
- neighbouring-cell, row-number and opening-hour inference is impossible;
- segment ordinals keep several entries in one table cell distinct during
  adjacent differencing;
- no source text, date, filename, path, key or mapping reaches the projection,
  aggregate output, exception or test receipt;
- mapped-ratio, stable-linkage, change, interval and zero-denominator decisions
  use closed vocabularies; and
- all 122 predecessor privacy/H5/H15 controls remain unchanged and passing.

Ruff, compilation, PowerShell parsing, source-boundary scans and Git diff checks
must pass before Phase A.

## One fresh local measurement

Only after the planning commit and complete synthetic verification may the
controller bind the unchanged literal source root:

`local_data/historical-diary-trove/raw/pilot_01`

The new ignored attempt root is:

`local_data/historical-diary-trove/measured-probes/2026-08-24-time-axis-v1`

Phase A must create one fresh manifest using the accepted non-recursive,
non-reparse, first-80 chronological selector, 8 MiB per-file and 128 MiB total
caps, full controller/extractor SHA-256 bindings and exact readback. It may make
aggregate-only metadata corrections but cannot open content until one manifest
passes.

Phase B may run at most once. It opens only the 80 bound documents read-only in
one owned invisible Word process, reduces private text in memory, writes no raw
text, persists no key or mapping, removes its manifest and private projection,
and retains only an ignored aggregate reading and cleanup receipt. Failure
cannot trigger an automatic content retry.

## Typed decision

`blocked` is mandatory for any root, manifest, digest, Word, cleanup, raw-output
or leakage failure. `revision_required` is mandatory when containment holds but
the mapper lacks a trustworthy time axis, stable linkage or adjacent motion.

`locally_restricted_candidate` requires all of:

- exactly 80 opened and parsed snapshots from the fresh manifest;
- zero source-value leakage and complete process/key/mapping cleanup;
- at least three distinct mapped minutes and one positive interval mode;
- no decreasing per-cell anchor sequence;
- at least 25% of structural occupancy observations mapped by an explicit
  same-cell anchor;
- nonzero stable linkage and nonzero adjacent change; and
- an exact aggregate result that makes no anonymity or downstream-use claim.

Even that strongest result authorises only ignored local research retention.
The first-use gate remains closed and a later, separately accepted promotion
operation must evaluate an actual candidate artifact.

## First-use gate boundary

The frozen gate applies at the earliest material boundary: before a
historical-derived structure is written as a reusable repository fixture,
scenario, replay, corpus, memory object or product-facing test. It does not
apply to purely authored-synthetic tests or aggregate local measurement.

Its later evaluator must require a full 40-character accepted source commit,
zero forbidden fields, source-independent synthetic identities, shifted or
relative dates, no persisted local HMAC token/key/mapping, an explicit
structural-utility purpose, deterministic leakage checks and a bounded artifact
class. A whole-day or near-lossless replay is not silently equivalent to a tiny
scenario and needs its own declared artifact class. No LLM may free-write an
admission result; the gate's decision is a typed deterministic value.

## Acceptance

Pass requires the five-source receipt, valid latch, recorded serial lane
dispositions, frozen plan/threat/gate contract, synthetic-first verification,
one fresh exact manifest, at most one content run, complete cleanup, truthful
aggregate evidence and preservation of every existing authority ceiling. A
contained `revision_required` result may close truthfully but grants no
scenario work.

Closeout must use the governance clockwork, write the paired lay/technical Yuri
summary and send the non-PHI Pushover notification before continuing to the
dependency-satisfied successor.

## Parallelism assessment

- **DeepSeek:** declined with negative leverage. Its native harness remains
  paused, silent Claude Code fallback is forbidden and no external worker may
  receive private Diary material or the one-run lease.
- **Gemini:** not applicable with neutral leverage. Provider/model transmission
  is forbidden, and deterministic synthetic/privacy gates own review.
- **Native subagents:** declined with negative leverage. The manifest, Word
  process, paragraph stream, ephemeral keys and one-run counter form one serial
  private state.
- **GPT Sol:** owns planning, implementation, synthetic verification, exact
  local run, acceptance, cleanup, Git and closeout.

Reassess only if deterministic verification exposes a genuinely separable,
wholly synthetic package before content access; private inputs remain
non-delegable.

## Closed surfaces

No new root, dense day, recursion, reparse traversal or byte cap; no raw text,
identity, note, contact value, filename, exact date/timestamp, key or mapping in
Git, stdout or conversation; no provider, network, model, telemetry, clipboard
or external release; no fixture/scenario/replay/corpus/memory/RAG promotion; no
product runtime, route, API, client, database or configuration; no ordinary
practice activation; no production, deployment, release, Pages, protected
evidence or protected-ref movement. Local/origin `master` and
`handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage explicit paths only.
