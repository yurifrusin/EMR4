# Raisa local-only bounded historical Diary snapshot measured privacy probe — plan

Date: 2026-08-24

Timestamp: 2026-08-24T03:08:20+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_plan`

Operation: `raisa-local-only-bounded-historical-diary-snapshot-measured-privacy-probe`

Planning source HEAD: `7338b2165245255fdf63de80c651206a97e6d2bd`

Reasoning level: Extra High. This is the first newly authorised local read of
historical private Diary snapshots under the accepted privacy gate. The run
must preserve useful longitudinal mechanics while ensuring that raw identity,
text, paths and exact source dates never enter Git, a provider, another model
or conversational output.

## Decision and objective

Run one bounded, provider-free, local-only privacy-and-utility measurement on
the already documented H15 leaf root:

`local_data/historical-diary-trove/raw/pilot_01`

The root is fixed before enumeration. The ignored attempt root is:

`local_data/historical-diary-trove/measured-probes/2026-08-24-boundary-v1`

The tranche may retain a pseudonymised near-lossless grid-cell trajectory only
inside that ignored attempt root. Committed evidence is aggregate and non-PHI.
The strongest decision is `locally_restricted_candidate`; it grants no fixture,
memory, provider, model, product or publication use.

The predecessor Sol acceptance contains one sentence fragment introduced while
recording register revision 654. Correct that prose without changing its
verdict, source, evidence or authority.

## Two-phase execution

### Phase A — exact metadata binding

Implement a controller that accepts only the literal root and attempt root
above. Before opening Word or reading document bytes it must:

1. resolve the root and prove it remains under the ignored historical-Diary
   tree;
2. reject a symlink, junction or reparse point at the root or any selected
   input;
3. enumerate non-recursively and admit only regular `.doc` files larger than
   the legacy OLE header minimum and no larger than 8 MiB each;
4. parse observation timestamps from filenames entirely in local memory using
   a closed family of year-first and day-first numeric timestamp shapes;
5. emit only aggregate filename-shape and timestamp-parse counts, never a name,
   stem, exact timestamp, date or path;
6. select exactly one densest parsed source day, resolving a tie
   deterministically, then select the first 80 chronologically consecutive
   observations from that day;
7. reject fewer than two selected observations, duplicate observation times,
   any selected parse failure, more than 80 files, more than 128 MiB total or
   any file larger than 8 MiB;
8. write an ignored exact manifest containing the local source paths, relative
   sequence, exact local timestamps, sizes and metadata readback; and
9. bind the controller, PowerShell extractor and Python privacy core by their
   full SHA-256 digests.

Phase A prints only a closed aggregate receipt. It performs no Word automation,
content read, hash of document bytes or text extraction. Phase B cannot start
unless the manifest readback is exact and unchanged.

If the closed filename parsers cannot bind 80 consecutive observations, the
run returns `revision_required` with only aggregate shape counts. No raw name is
shown to GPT Sol; any parser repair must be inferred from those aggregate
shapes or use a separately frozen local deterministic diagnostic.

### Phase B — read-only local measurement

After Phase A passes, launch Microsoft Word with visibility off, alerts off and
macro automation security forced disabled. Open only the 80 bound files,
read-only, in manifest order. Close and release each document before the next.

The extractor sends document structure and cell text through a local in-memory
pipe to the exact repository Python interpreter. It writes no raw or extracted
text file. The Python core must immediately reduce the private payload to:

- relative 30-second observation intervals;
- synthetic resource ordinals from table/column positions;
- grid row/column and derived time-of-day where a time label maps the row;
- closed formatting, content-presence, note/sensitivity and identifier-category
  buckets;
- domain-separated HMAC-SHA-256 content/linkage stand-ins created from an
  ephemeral in-memory key; and
- add, remove, move, formatting-change and same-position replacement events
  across adjacent observations.

The ignored private-derived projection may contain only those fields and
stand-ins. It may not contain source text, direct identities, contact values,
external identifiers, names, original filenames, paths, exact source dates or
timestamps, a key, a mapping table or reversible hashes.

## Measured privacy and utility reading

The aggregate result must report integer numerators and denominators for:

- opened, parsed and rejected snapshots;
- source cell observations and admitted structural occupancy records;
- source identity/contact/note detector category counts without matched values;
- output leakage detections;
- records with mapped time/resource structure;
- stable stand-ins observed in more than one snapshot;
- exact adjacent change counts by closed type;
- equivalence-class sizes over time/resource/format/note buckets;
- unique record and trajectory counts;
- rare trajectory frequency;
- record- and trajectory-linkage attack successes/trials; and
- cross-key structural differencing successes/trials.

`blocked` is mandatory for any boundary, manifest, readback, raw-output or
leakage failure. `revision_required` applies when the pipeline remains contained
but cannot parse enough snapshots, map useful scheduling structure, recover any
adjacent change or demonstrate stable linkage. `locally_restricted_candidate`
requires zero raw leakage, exact cleanup/key disposal, at least two parsed
snapshots, nonzero stable linkage and nonzero adjacent changes. Linkability may
remain high and must be reported; it is not hidden by the local-only decision.

## Implementation and verification

Create:

- `orchestration_harness/historical_diary_local_measured_privacy_probe.py` for
  strict private-input models, projection, differencing, risk, utility,
  leakage and typed decisions;
- `scripts/historical_diary_local_measured_privacy_probe.ps1` for the exact
  two-phase binding and Word read-only controller; and
- `tests/test_raisa_local_only_bounded_historical_diary_snapshot_measured_privacy_probe.py`
  for wholly authored synthetic hostile tests.

Tests must cover closed models and vocabularies, timestamp shapes, path escape,
reparse points, recursion, type/count/byte caps, manifest drift, parser-digest
drift, raw-output attempts, detector categories, HMAC stability/key separation,
cell projection, time/resource mapping, all event types, equivalence/uniqueness/
rarity/linkage/differencing, zero denominators, decisions and cleanup. Source
scans prove no provider/network/product/database import and no raw text logging.

Before archive enumeration, pass Ruff, compileall, PowerShell parse, synthetic
tests and the unchanged 86 privacy/H5/H15 controls from the accepted gate. Then
run Phase A once. Only a passing binding may launch Phase B once. Any failure
stops without an automatic content retry; a deterministic correction requires
readback of the exact failure and the narrowest in-scope repair.

## Acceptance

Pass requires:

1. the fresh five-source receipt and valid exact subgate latch;
2. the recorded serial DeepSeek, Gemini and native-subagent dispositions;
3. synthetic hostile verification before archive enumeration;
4. one exact Phase A ignored manifest satisfying every count/path/byte/digest
   constraint before document content access;
5. at most one Phase B run over exactly the bound files with complete Word,
   process, key and temporary-resource cleanup;
6. zero raw/private value in stdout, committed files or the conversation;
7. a truthful typed result with scoped privacy/linkability and utility counts;
8. no change to H5/H15, product/runtime or downstream-use authority;
9. clockwork closeout, paired Yuri summary and non-PHI Pushover notification;
   and
10. unchanged protected refs and preservation of every unrelated untracked
    file.

## Parallelism assessment

- **DeepSeek:** declined with negative leverage. Its native harness is paused,
  no silent Claude Code fallback is permitted, and no external worker receives
  raw or private-derived Diary material.
- **Gemini:** not applicable with neutral leverage. Provider, network and model
  transmission are forbidden for the run and its review.
- **Native subagents:** declined with negative leverage. The exact ignored
  manifest, Word process, ephemeral key and local projection are one serial
  private state; no separable package may receive it.
- **GPT Sol:** owns code, synthetic tests, exact local execution, aggregate
  review, acceptance, cleanup, Git and clockwork closeout.

## Closed surfaces

No access outside the exact root/day/manifest; no recursion or reparse
traversal; no raw/extracted text, identity, filename, exact timestamp, key or
mapping commit or display; no provider, network, model prompt, telemetry,
clipboard or external release; no fixture, memory, RAG or GraphRAG promotion;
no product runtime, route, API, client, database or configuration change; no
ordinary-practice enablement; no production, deployment, release, Pages,
protected evidence or protected-ref movement. Local/origin `master` and
`handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
every unrelated untracked file. Stage explicit paths only.

## Phase A recovery addendum

The first metadata-only bind at exact controller source
`3d14337bb5428f2f388dfa97320abac86300695d` returned the closed code
`candidate_file_size_invalid`. It created no attempt root or manifest and
opened no document content.

The size rule is clarified without widening admission: regular `.doc` files at
or below 4,096 bytes or above 8 MiB are counted in separate aggregate exclusion
buckets and never become candidates. Exactly 80 in-envelope observations are
still mandatory, each selected file is rechecked against the cap in the strict
manifest and before Word, and the selected total remains capped at 128 MiB.
This prevents an unadmitted housekeeping or unrelated large document from
vetoing an otherwise exact bounded day while making it impossible for either
class to reach content processing. One corrected metadata-only bind is
authorised; it is not a content retry.

The corrected size-aware bind at exact source
`f449c536194a4760b9fc58db42d29fe0e6df87e7` then returned an aggregate-only
`timestamp_binding_revision_required`: all 582 in-envelope files belonged to
one six-numeric-group shape, with zero timestamp successes. It again created no
attempt root or manifest and opened no content. The parser may therefore join
all numeric groups only when their total is exactly 14 digits, then apply the
unchanged unambiguous four-digit-year year-first/day-first calendars. Extra or
missing digits, two-digit-year ambiguity and multiple valid interpretations
remain rejected. One further metadata-only binding is authorised from this
shape-derived repair; Phase B remains closed until it passes.

That repaired source still returned zero parses, proving that the coarse
alternating digit/separator class does not establish a 14-digit total. A
separately frozen metadata diagnostic may add only aggregate numeric-group
length signatures and total-digit-count distributions. These are filename
shape, not values: they contain no numeric group value and no filename, date
or path. The next parser decision must derive solely from this reading and
remain unambiguous before any manifest or content operation.

The frozen diagnostic at exact source
`7fc5f0568fe9e456d2e9c7f9aedbd49e92b18e21` reports that all 582 admissible
files use six numeric groups: 477 have lengths `2-1-2-2-2-2` and 105 have
`2-1-2-2-2-1`; the two five-group shapes are exactly the undersized exclusions.
The next parser may treat group three as a two-digit year, groups four through
six as time with a closed trailing AM/PM token, and test only day-month-year
and month-day-year. It may bind only if exactly one convention parses all 582
admissible files. A per-file guess or a tie is forbidden. Two-digit years are
restricted to 2000 through 2020, matching this frozen historical archive
scope. Phase B remains closed until one global convention and exactly 80
observations bind.

The resulting source `2fd54a97f95aaec5a0601c3b0107fa27bf2fd5dc`
reported zero coverage for both conventions, still without creating a manifest
or reading content. The same aggregate widths support the omitted separated
year-first form `YY-M-D HH-MM-SS`. Add that one closed candidate. It remains
subject to the identical 2000-2020 year bound and sole archive-wide
full-coverage rule; no convention is chosen from plausibility alone.

Exact source `62dc37d53a19ba5d1dfbf4ca01a47f1dc351123c` then appeared to produce a
two-convention full-coverage tie. The pre-rerun synthetic metadata-concordance
test rejected that reading: `month_day_two_digit_year` was indented under the
year-first branch and reused its year, so the label did not represent its
declared convention. No manifest or content read occurred. Preserve the
reading as rejected diagnostic evidence and correct only that candidate
construction.

Phase A already reads each file's modification timestamp and H15 historically
used that metadata for ordering. A genuine tie may therefore be resolved only
if exactly one correctly constructed full-coverage convention lies within 24
hours of modification time for every admissible file. The public reading
exposes only convention counts and the fixed threshold, never a time, date,
delta per file or filename. Zero or more than one metadata-concordant
convention remains `revision_required` unless exactly one full-coverage
convention exists independently.
