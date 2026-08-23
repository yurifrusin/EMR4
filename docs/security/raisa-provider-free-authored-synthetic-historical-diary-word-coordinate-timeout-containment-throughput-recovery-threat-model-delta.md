# Raisa provider-free authored-synthetic historical Diary Word-coordinate timeout containment and throughput recovery — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T05:52:11.6529803+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_threat_delta`

Operation: `raisa-provider-free-authored-synthetic-historical-diary-word-coordinate-timeout-containment-throughput-recovery`

## Assets

- the user's pre-existing Word process set;
- one or two exactly owned synthetic-proof Word processes;
- ignored process-control and count-only progress objects;
- newly authored generic synthetic documents;
- the one-way historical content terminal and closed first-use gate; and
- repository history, protected refs and unrelated untracked files.

## Threats and controls

### Timeout strands a Word process

Threat: Python terminates PowerShell before its `finally` block, leaving an
owned Word process alive.

Control: PowerShell writes PID, `WINWORD` class and UTC start ticks immediately
after isolation. The parent invokes a dedicated cleanup script on timeout,
abnormal exit or invalid output and verifies exact absence.

### Cleanup kills the user's Word process

Threat: process-name cleanup cannot distinguish the owned process from a
pre-existing user process.

Control: cleanup requires exact PID, process class and start ticks. Missing,
invalid or mismatched identity fails closed. Broad process-name stopping and
baseline-difference guessing are forbidden.

### The control or progress file leaks private structure

Threat: a durable sidecar becomes a covert document/path/text/coordinate log.

Control: strict extra-forbid schemas admit process identity only in the control
object and bounded integer counts plus closed elapsed/rate buckets only in
progress. Tests scan all output schemas and source writes for forbidden fields.
This tranche uses no historical document.

### Progress reveals individual document timing

Threat: exact timestamps or per-document durations could fingerprint a future
source sequence.

Control: progress exposes aggregate completed count and coarse elapsed/rate
buckets only. It has no document identity, exact timestamp or per-document
series in retained evidence.

### Synthetic benchmark silently touches the archive

Threat: reused binding code enumerates the historical root while claiming a
synthetic run.

Control: the generator and benchmark accept one literal synthetic root outside
the historical subtree, build an exact manifest from files they just created,
and reject any path outside that root. Source scans and access spies prove the
historical root is never enumerated or opened.

### Synthetic success is treated as empirical utility

Threat: process and throughput evidence is promoted to a claim about real
Diary mappings or reusable scenarios.

Control: the strongest result is only a provider-free recovery candidate for
a separately planned measurement. Mapping utility, privacy admission and first
use remain unmeasured or closed.

### Recovery becomes a timeout increase without diagnosis

Threat: a larger deadline hides a stalled child and makes cleanup less
reliable.

Control: this tranche does not change historical-run authority or repeat the
run. It first adds typed failure, exact cleanup and a measured synthetic rate;
only a later plan may choose a new bound from evidence.

## Residual risk

Synthetic `.docx` opening and layout cost may differ from decade-old `.doc`
files. A passing rate therefore proves controller observability and a bounded
synthetic throughput floor, not the completion time of a future historical
slice. Windows process start-time resolution and COM shutdown races remain
possible, so identity mismatch blocks rather than broadening cleanup.

## Authority ceiling

This delta permits deterministic tests and exactly two serial authored-
synthetic Word-process proofs. It permits no historical data access, reusable
historical-derived artifact, provider/model transmission, product/runtime,
database, ordinary-practice activation, production, deployment, release,
Pages, protected evidence or protected-ref movement.
