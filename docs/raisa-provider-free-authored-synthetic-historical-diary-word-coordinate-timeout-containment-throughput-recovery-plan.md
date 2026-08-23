# Raisa provider-free authored-synthetic historical Diary Word-coordinate timeout containment and throughput recovery — plan

Date: 2026-08-24

Timestamp: 2026-08-24T05:52:11.6529803+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_plan`

Operation: `raisa-provider-free-authored-synthetic-historical-diary-word-coordinate-timeout-containment-throughput-recovery`

Planning source HEAD: `5ccde48c8dbc42aa3931458f2b2a34e03126c0be`

Reasoning level: Extra High. This recovery chooses the durable process-identity,
timeout and throughput controls that would bound a later private measurement.
It may not inspect or reuse any historical document.

## Objective and authority

Recover three operational controls exposed by the accepted one-run timeout:

1. a typed `word_extractor_timeout` instead of the generic
   `internal_local_probe_failure`;
2. exact parent-owned cleanup of the one Word process created by the child,
   even when PowerShell is interrupted; and
3. count-only progress and throughput evidence sufficient to choose a truthful
   bound for a separately planned future measurement.

All occupied inputs are newly authored synthetic Word documents. The literal
historical root, its attempt roots and every historical file are denied to
this tranche. The historical-derived first-use gate remains present and closed
but does not apply to wholly authored-synthetic verification.

## Exact process-control seam

The parent creates exact ignored control and progress paths and passes both to
PowerShell. Immediately after Word process isolation succeeds, PowerShell
writes a strict control object containing only:

- schema version;
- process ID;
- Word process start time in UTC ticks; and
- `WINWORD` as the closed process class.

The object contains no document, filename, path, text, time label, page or
coordinate value. Normal PowerShell cleanup removes it only after the exact
owned process is absent.

On `subprocess.TimeoutExpired`, abnormal child exit or invalid child output,
the Python parent invokes one dedicated cleanup script with the literal
control path. The cleanup script may stop a process only when PID, process
class and UTC start ticks all match. A missing or mismatched identity cannot
fall back to process-name killing; it returns a typed cleanup failure. It polls
the exact PID for at most ten seconds and never touches a pre-existing Word
process.

The parent then records:

- `word_extractor_timeout` when timeout cleanup is complete;
- `word_extractor_timeout_cleanup_failed` when exact absence is unproved; or
- the existing typed child failure with its exact cleanup disposition.

The content terminal remains one-way and does not authorize retry.

## Count-only progress and throughput

PowerShell atomically replaces an ignored progress object after initialization,
Word isolation and each completed synthetic document. Its exact vocabulary is:

- `stage`: `initialized`, `word_isolated`, `document_completed`, `cleanup`;
- total and completed document counts;
- table-cell, structural-segment, coordinate-attempt and explicit-story-anchor
  integer counts;
- `elapsed_bucket`: `under_30_seconds`, `30_to_119_seconds`,
  `120_to_299_seconds`, `300_to_899_seconds` or
  `900_seconds_or_more`; and
- `coordinate_rate_floor_bucket`: `not_available`, `under_1_per_second`,
  `1_to_3_per_second`, `4_to_7_per_second`, `8_to_15_per_second` or
  `16_or_more_per_second`.

No exact elapsed time, document ordinal beyond aggregate completed count,
filename, path, timestamp, source text, time value, page, coordinate, distance,
key or mapping may appear. Schema, monotonicity and upper bounds are validated
before the reading can inform acceptance.

## Synthetic-first verification

Before occupied Word automation, deterministic tests must prove:

- exact control/progress schemas and rejection of extra or inconsistent fields;
- `TimeoutExpired` maps to the typed timeout reason;
- the parent cleanup seam is invoked on timeout, abnormal exit and invalid
  output and is not invoked after complete child cleanup;
- cleanup mismatch never broad-kills by process name;
- terminal, aggregate and cleanup evidence distinguish successful cleanup from
  unproved cleanup;
- progress counts are monotonic, bounded and value-free;
- the existing zero/four-point, tie, cross-page, manual-line and no-fallback
  mapper controls remain exact;
- all 175 provider-free historical-Diary controls remain passing; and
- Ruff, compileall, PowerShell parsing, source-boundary scans and Git diff
  checks pass.

## Two occupied authored-synthetic proofs

Only after deterministic admission may two local Word process proofs run,
serially:

1. **Timeout containment proof.** Create one isolated Word process without
   opening a document, write its exact control identity, intentionally hold the
   child beyond a two-second parent timeout, and prove the cleanup script
   removes that process while preserving every pre-existing Word process.
2. **Throughput proof.** Generate twelve `.docx` documents under
   `local_data/authored-synthetic-diary-word-coordinate-recovery/` with
   14 table cells and 12 structural paragraphs per cell plus 24 complete story
   time anchors. Open only those exact manifest-bound documents read-only in
   one isolated invisible Word process. The proof has a 300-second ceiling.

The synthetic generator uses fixed generic content tokens and `python-docx`;
it must not enumerate any other root. Documents, manifest, control, progress,
private extraction, keys and mappings are removed after the proof. Only a
non-PHI aggregate reading may enter Git.

## Acceptance

`passed` requires:

- all deterministic and unchanged controls passing;
- typed timeout and abnormal-child classifications with no generic internal
  timeout reason;
- the timeout proof removing exactly one owned Word process and preserving the
  pre-existing process set;
- throughput proof opening 12/12 documents, attempting at least 2,000 segment
  coordinates and observing at least 250 explicit story anchors;
- completion below the 300-second terminal with a non-`not_available`
  coordinate-rate floor bucket;
- monotonic count-only progress, zero source/private value leakage and complete
  cleanup; and
- zero historical archive enumeration or content access.

`revision_required` applies when safety and cleanup hold but the synthetic
throughput floor is not reached. `blocked` applies to process-identity
ambiguity, pre-existing process loss, raw/value output, unproved cleanup,
historical access or any authority breach.

The strongest result is a provider-free recovery candidate for a separately
planned new local measurement. It grants no such measurement, historical-
derived artifact or downstream use.

## Parallelism assessment

- **DeepSeek:** declined with negative leverage. The native harness remains
  paused, no silent Claude fallback is allowed, and one Word/control/progress
  state is serial.
- **Gemini:** not applicable with neutral leverage. The contract is
  deterministic, provider-free and has no independent semantic-veto need.
- **Native subagents:** declined with negative leverage. Shared process
  identity and occupied proofs cannot be partitioned safely.
- **GPT Sol:** owns design, implementation, verification, both occupied
  synthetic proofs, acceptance, cleanup, Git and closeout.

Reassess only if a later wholly static separable package appears. No worker may
receive historical data or own an occupied Word process.

## Closed surfaces

No historical archive enumeration/content, historical-derived fixture or
scenario, provider/network/model call, product/patient/appointment/clinical
data, product/runtime/database/API/client/configuration change,
ordinary-practice activation, production, deployment, release, Pages,
protected evidence or protected-ref movement. Local/origin `master` and
`handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and all
unrelated untracked files. Stage explicit paths only.
