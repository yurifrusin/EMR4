# Raisa local-only historical Diary document-story time-coordinate recovery rehearsal — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T04:58:35.7619006+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_threat_delta`

Operation: `raisa-local-only-historical-diary-document-story-time-coordinate-recovery-rehearsal`

## Assets

- 80 raw historical Diary snapshots and their story/table text;
- explicit time labels, rendered page/vertical positions and rare trajectories;
- ignored manifest, private pipe/projection and ephemeral HMAC keys;
- the owned Word process and one-content-run terminal;
- default-deny historical-derived first-use gate; and
- repository history, protected refs and unrelated untracked files.

## Threats and controls

### Main-story text expands the private payload

Threat: extracting the document story sends names, notes or other non-table PHI
through the pipe or into an error.

Control: PowerShell parses complete time tokens locally and emits only integer
minutes plus private coordinates. No main-story raw text enters Python, files,
stdout, exceptions, Git, models or providers.

### Layout coordinates become identifying output

Threat: page and vertical positions reveal a distinctive source layout or are
retained as a reversible mapping aid.

Control: coordinates are private input only, quantised to integer
quarter-points, used inside one projection call and omitted from every private
projection and public aggregate. Cleanup retains no coordinate table.

### Nearest-label mapping invents time

Threat: a distant or cross-page label is selected because it is the best
available candidate.

Control: same adjusted page is mandatory; distance must be at most four points;
no candidate means unmapped. Row, column, ordinal, opening hour, interval mode,
filename and metadata confer no fallback time.

### Coordinate tie hides ambiguity

Threat: two time labels are equally near and an arbitrary iteration order picks
one.

Control: deduplicate identical `(position, minute)` readings, then require one
unique nearest minute. A different-time tie is unmapped and counted by a closed
reason.

### Manual line breaks inherit the wrong baseline

Threat: several visual lines inside one Word paragraph receive the first line's
coordinate.

Control: only the first subdivision may use the paragraph coordinate; manual
subdivisions without an independently supplied position are explicitly
unavailable and remain unmapped.

### Word layout is unstable or unavailable

Threat: hidden/read-only Word lacks pagination, returns invalid positions or
depends on ambient printer state.

Control: page and vertical values must pass bounded readback for each admitted
anchor/segment. Unavailable coordinates cannot map. The aggregate reports
availability and mapping ratios; a contained low-utility result requires
revision and cannot be retried in this tranche.

### A successful local clock opens scenario use

Threat: time recovery is cited as authority to commit historical-derived
fixtures or tune Raisa.

Control: the first-use gate remains closed and candidate-specific. This tranche
can retain only aggregate ignored-local evidence; no reusable artifact is
created.

### Repeated empirical attempts overfit the slice

Threat: coordinate tolerance or selection is adjusted after each archive read.

Control: four points, same-page, unique-nearest and all rejection rules are
frozen before access. One fresh terminal permits one content run only. Any
result closes truthfully and the next decision must use a separately published
operation.

## Residual risk

Rendered proximity can establish that a structural text segment is visually
aligned to a time label, but it cannot prove the segment is a patient booking
rather than a break, header, roster note or composite entry. Rare time/resource
trajectories may remain linkable. The result therefore remains structural and
local; semantics and reusable scenario admission stay separately gated.

## Authority ceiling

This delta permits one synthetic-first document-story/coordinate mapper and at
most one fresh 80-file local measurement. It grants no historical-derived
artifact, provider/model transmission, product runtime, database,
ordinary-practice activation, production, deployment, release, Pages,
protected evidence or protected-ref movement.
