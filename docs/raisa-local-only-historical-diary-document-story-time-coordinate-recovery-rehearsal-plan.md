# Raisa local-only historical Diary document-story time-coordinate recovery rehearsal — plan

Date: 2026-08-24

Timestamp: 2026-08-24T04:58:35.7619006+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_plan`

Operation: `raisa-local-only-historical-diary-document-story-time-coordinate-recovery-rehearsal`

Planning source HEAD: `4cfe27ef5ac029c2ebce4a3cdcae5f0d211ab4f8`

Reasoning level: Extra High. This tranche adds local Word-rendered layout
coordinates to private processing. It must recover explicit time-of-day without
persisting coordinates, widening historical access or turning a successful
measurement into scenario admission.

## Decision and objective

The accepted predecessor proved that 12,557 table-cell segments contain zero
explicit time anchors, while committed H3/H4 aggregate evidence records 78
time-like tokens, 37 unique time-like tokens and a 10-minute mode in the whole
Word document. Recover time by extracting only complete time tokens from the
document main story outside tables and associating them with table-cell
paragraphs through Word's page and vertical-position readings from the same
open read-only document.

No time may be inferred from row/column, paragraph ordinal, filename,
modification time, expected clinic hours or the known interval mode. The
existing first-use gate remains closed; this tranche may produce only an
ignored local aggregate reading.

## Private extraction model

The local PowerShell extractor may add only these private in-memory fields:

- for each complete story time token outside a table: `time_minute`, adjusted
  page ordinal and vertical position quantised to quarter-points;
- for each table-cell paragraph segment: its bounded segment ordinal, adjusted
  page ordinal and quarter-point vertical position; and
- a closed `coordinate_available` boolean when Word supplies both values.

The main-story raw paragraph text must never cross the PowerShell/Python pipe.
PowerShell performs the exact full-token time parse and releases only the
integer minute plus private coordinates. Table-cell text remains inside the
existing capped private pipe for immediate HMAC/bucket reduction.

Manual-line subdivisions that cannot receive their own Word coordinate remain
`coordinate_available=false`; a parent paragraph coordinate cannot be reused
as a guess. Paragraph/coordinate counts, ordinals and schema are validated
exactly before projection.

## Closed coordinate mapper

For each structural table-cell segment:

1. consider only story anchors from the same adjusted page;
2. compute absolute vertical distance in integer quarter-points;
3. admit candidates no farther than 16 quarter-points (4 points);
4. select only one unique nearest `(vertical_position, time_minute)` anchor;
5. allow duplicate identical anchor readings but reject a nearest tie carrying
   different minutes;
6. label missing, unavailable, over-distance and ambiguous coordinates with
   separate closed reason counts; and
7. immediately discard coordinate values after time mapping.

The private projection may contain `time_minute` and the closed mapping label
`explicit_story_same_page_coordinate`, but no page, vertical position,
distance, story anchor set or coordinate table. Public evidence contains only
integer anchor/mapped/unmapped counts, the known time interval mode and closed
distance buckets, never source coordinates or values.

## Synthetic-first verification

Before manifest creation or archive content access, authored-synthetic tests
must prove:

- strict story-anchor and segment-coordinate schemas, paired availability and
  sequential ordinals;
- exact time parsing, AM/PM handling and rejection of embedded time-like text;
- same-page unique-nearest mapping at zero and boundary distance;
- rejection just outside four points, cross-page candidates and different-time
  nearest ties;
- identical duplicate anchors do not create false ambiguity;
- manual-line subdivisions without coordinates remain unmapped;
- no row, column, ordinal, opening-hour, interval-mode or filename fallback;
- projection/output contains no story text, page, coordinate, distance, key,
  mapping, filename, path, date or source value;
- segment-position differencing, stable linkage, privacy and one-run cleanup
  remain exact; and
- all 145 predecessor focused/privacy/H5/H15 controls remain passing.

Ruff, compileall, PowerShell parsing, source-boundary scans and Git diff checks
must pass before Phase A.

## One fresh local measurement

The literal source root remains:

`local_data/historical-diary-trove/raw/pilot_01`

The fresh ignored attempt root is:

`local_data/historical-diary-trove/measured-probes/2026-08-24-story-coordinate-v1`

Phase A retains the accepted non-recursive, non-reparse, first-80
chronological selector, 8 MiB per-file and 128 MiB total caps, exact controller
and extractor SHA-256 bindings and strict readback. It performs no content read.

Only after all synthetic/static controls pass may Phase B run once. It opens
only the 80 bound files in one owned invisible read-only Word process. The
content-run terminal is written before Word launch and prohibits a second run.
Cleanup removes the manifest, private projection, coordinates, keys and
mappings whether the result passes, requires revision or blocks. Only the
ignored aggregate reading and cleanup/terminal receipts remain.

## Typed decision and acceptance

`blocked` is mandatory for any root, manifest, digest, Word-control, schema,
raw-output, leakage or cleanup failure. `revision_required` applies when
containment holds but explicit story anchors, coordinate mapping, stable
linkage or adjacent motion are insufficient.

`locally_restricted_candidate` requires:

- exactly 80 opened and parsed snapshots in the sole content run;
- zero source-value leakage and complete Word/key/mapping/coordinate cleanup;
- at least three explicit story anchors and three distinct mapped minutes;
- a positive deterministic interval mode;
- at least 25% of structural occupancy segments mapped through a unique
  same-page anchor no farther than four points;
- zero admitted ambiguous/cross-page/over-distance mapping;
- nonzero stable linkage and adjacent changes; and
- a truthful aggregate result with no anonymity or downstream-use claim.

Even the strongest result grants only ignored local research retention. The
first-use gate remains `closed_pending_candidate_specific_evaluation`; no
fixture, scenario, replay, corpus, memory or product test may be created here.

## Parallelism assessment

- **DeepSeek:** declined with negative leverage. The native harness is paused,
  no silent Claude Code fallback is permitted and no external worker may
  receive private Diary text, coordinates or the one-run lease.
- **Gemini:** not applicable with neutral leverage. Provider/model transmission
  is forbidden and deterministic tests own the review surface.
- **Native subagents:** declined with negative leverage. Manifest, Word story,
  cell coordinates, ephemeral keys and content terminal form one serial
  private state.
- **GPT Sol:** owns design, implementation, synthetic verification, exact local
  run, acceptance, cleanup, Git and closeout.

Reassess only if a wholly synthetic separable package appears before archive
access; private inputs and coordinate evidence remain non-delegable.

## Closed surfaces

No new root/day, recursion, reparse traversal or byte cap; no raw text,
identity, note, contact value, filename, exact date/timestamp, page, coordinate,
distance, key or mapping in Git/stdout/conversation; no provider, network,
model, telemetry, clipboard or external release; no historical-derived
fixture/scenario/replay/corpus/memory/RAG promotion; no product runtime, route,
API, client, database or configuration; no ordinary-practice activation; no
production, deployment, release, Pages, protected evidence or protected-ref
movement. Local/origin `master` and `handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
all unrelated untracked files. Stage explicit paths only.
