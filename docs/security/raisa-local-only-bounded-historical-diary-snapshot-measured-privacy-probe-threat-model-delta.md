# Raisa local-only bounded historical Diary snapshot measured privacy probe — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T03:08:20+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_threat_delta`

Operation: `raisa-local-only-bounded-historical-diary-snapshot-measured-privacy-probe`

## Assets

- up to 80 raw historical Diary Word snapshots and their filenames;
- direct identities, contact details, external identifiers and free text;
- exact clinic dates, observation timestamps and rare longitudinal patterns;
- scheduling grid structure and state-change utility;
- ignored exact manifest, pseudonymised projection and local risk readings;
- ephemeral HMAC key material and linkage stand-ins;
- Word automation, parser executables and cleanup state; and
- the repository, fixed protected refs and unrelated untracked files.

## Threats and controls

### Metadata contact becomes content access

Threat: choosing a day opens or hashes documents before the exact manifest is
bound.

Control: Phase A uses non-recursive name/attribute enumeration only and contains
no Word automation or document-byte read. Phase B requires an exact immutable
manifest readback and parser digests.

### Filename or timestamp leakage

Threat: a filename contains a person label, or an exact source date enters a
receipt, stdout, Git or the model context.

Control: filename parsing occurs only in local memory. Public output uses
aggregate shape counts and relative day/interval values. Raw names, paths,
dates and timestamps exist only in the ignored manifest and are never printed.
Unexpected shapes fail without echoing the name.

### Root escape or overbroad run

Threat: recursion, a junction, wildcard or repaired CLI argument expands the
80-file probe to the trove or another directory.

Control: the root and output are literal constants; resolved paths must remain
inside the ignored tree. Root and selected files reject reparse points.
Enumeration is non-recursive. File count, per-file and total-byte caps are
checked twice, and Phase B cannot accept CLI replacements.

### Word macro or external-content execution

Threat: opening a legacy `.doc` executes a macro, link, conversion prompt or
other active content.

Control: Word is invisible, alerts are disabled, automation security is forced
to disable macros, documents open read-only without conversion confirmation,
and the run uses no link update, save or print operation. Any inability to set
these controls blocks before the first document.

### Raw text persistence or process leakage

Threat: extraction writes a temporary text file, command line, exception,
traceback or log containing private text.

Control: cell text crosses only an inherited local stdin pipe and is reduced in
memory. The controller and core never place text in arguments, files, stdout or
exceptions. Errors use closed codes and counts. Raw buffers are released after
each document and cleanup removes every incomplete output.

### Pseudonymisation mistaken for anonymity

Threat: stable HMAC stand-ins obscure uniqueness and are treated as a safe
release.

Control: output remains private-derived and ignored. Equivalence, rarity,
record/trajectory linkage and cross-key structural differencing are explicit.
The strongest decision is local retention only and never claims anonymity.

### Utility lost through cell-level abstraction

Threat: the projection is safe but cannot recover useful check-in, change or
contention mechanics.

Control: preserve relative observation intervals, table/row/column, mapped
time, resource ordinal, formatting bucket, stable content linkage and adjacent
change types. Zero stable linkage, zero changes or inadequate time/resource
mapping returns `revision_required`, not a pass.

### Incorrect cell semantics

Threat: a grid cell is described as a patient or appointment when it may be a
header, break, roster marker or composite entry.

Control: this tranche labels records only as structural occupancy cells. It
does not infer patient identity, clinical meaning, appointment status or
command grammar. Later semantic promotion needs its own evidence gate.

### Multi-release reconstruction

Threat: two differently keyed projections can still be linked through rare
time/resource trajectories.

Control: measure cross-key structural uniqueness explicitly, retain only one
ignored attempt root and forbid a second release without a new operation.

### Cleanup or key failure

Threat: a crash leaves Word, raw buffers, an incomplete projection, a key or a
mapping available.

Control: use `finally` cleanup for each document and Word, generate the key
only in Python memory, never serialise mappings, remove incomplete outputs and
write a terminal cleanup receipt only after process and output readback.

### Downstream authority inflation

Threat: a useful local reading becomes fixture, model, product or production
approval.

Control: `locally_restricted_candidate` permits ignored local research
retention only. All fixture, memory, provider/model, product/runtime,
deployment, publication and protected-ref uses remain separately closed.

## Residual risk

The first cell-level parser may preserve workflow motion without separating a
person label from notes or recognising every appointment state. Local
pseudonyms also remain linkable through rare trajectories. Those limitations
are the point of this measured probe: they must be quantified truthfully before
any richer parser or downstream use is considered. A contained
`revision_required` result is a valid outcome and leaves raw material local.

## Phase A recovery delta

The first metadata bind showed that the exact leaf includes at least one `.doc`
outside the admission size envelope. The corrected selector counts undersized
and oversized exclusions without reading them. Neither class may enter the
candidate set, selected manifest, Word process or private pipe. Exact selected
file and total-byte caps remain independently enforced. This changes root-wide
veto ergonomics only; it adds no admitted byte or path.

The size-aware metadata retry exposed only an aggregate six-numeric-group
filename shape. Joining those groups is safe only at an exact 14-digit total;
the two four-digit-year calendar interpretations still must yield exactly one
valid timestamp. The parser never emits a group, value, date or filename, and
any extra numeric suffix remains a closed parse failure.
