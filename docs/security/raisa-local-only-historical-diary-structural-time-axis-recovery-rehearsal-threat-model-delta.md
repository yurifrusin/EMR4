# Raisa local-only historical Diary structural time-axis recovery rehearsal — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T04:21:32.7833986+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_threat_delta`

Operation: `raisa-local-only-historical-diary-structural-time-axis-recovery-rehearsal`

## Assets

- up to 80 raw private historical Diary snapshots;
- paragraph order, time labels, rare trajectories and appointment-like text;
- the fresh ignored manifest, private projection and ephemeral HMAC keys;
- the Word process and one-content-run lease;
- aggregate privacy/utility evidence and the default-deny first-use gate; and
- repository history, protected refs and unrelated untracked files.

## Threats and controls

### A guessed clock becomes evidence

Threat: row numbers, a plausible opening hour or a known 10-minute interval are
used to invent appointment times.

Control: a mapped segment requires a complete explicit time token earlier in
the same original Word table cell. Row, column, neighbouring cells, filenames
and assumed clinic hours confer no time. Fewer than three distinct mapped
minutes or a missing positive interval mode requires revision.

### Paragraph flattening corrupts positions

Threat: removing empty paragraphs shifts bookings onto the wrong time anchor,
or several entries in one table cell overwrite one another.

Control: preserve bounded empty segment positions and a segment ordinal; remove
only closed Word terminators. Segment ordinal participates in position and
diff identity. Hostile tests cover empty lines, manual breaks and multiple
entries.

### A malformed axis is accepted

Threat: a note that resembles a time or a decreasing sequence is treated as a
schedule.

Control: only full-token time syntax is an anchor. A backward per-cell sequence
fails closed; repeated times are explicitly allowed for double-booking shape.
The result reports closed anchor and rejection counts without values.

### Richer splitting increases leakage

Threat: splitting multi-paragraph cells makes names, notes or contacts easier to
log, persist or expose through exceptions.

Control: raw segments remain in the existing local pipe and Python memory only.
Tokens, buckets and integer structure replace them before output. Errors carry
closed codes; output leakage is scanned; the private projection and mapping are
deleted; no provider or subagent sees the stream.

### One content run is accidentally repeated

Threat: a contained utility failure triggers retries until a desirable reading
appears.

Control: the fresh attempt root and content counter admit at most one Phase B
run. Metadata binding may fail before content, but a content terminal is final
for this tranche and cleanup runs before closeout.

### Time utility silently opens downstream use

Threat: a successful local mapping is committed as a fixture or used to tune
Raisa without a separate privacy/utility decision.

Control: `locally_restricted_candidate` remains ignored-local only. The new
first-use gate is default-deny and triggers before any reusable
historical-derived scenario, fixture, replay, corpus, memory or product test.
This tranche cannot open it.

### The gate grows into blanket bureaucracy

Threat: every authored-synthetic test or local aggregate reading is forced
through a heavyweight promotion process.

Control: the gate attaches only at the first reusable historical-derived
artifact boundary. Purely authored-synthetic development and private aggregate
measurement are explicitly out of scope. Later evaluation is deterministic and
typed, not a free-form model form.

### A tiny scenario and whole-day replay are conflated

Threat: admission of one minimized structural scenario is cited as authority
for a near-lossless day trajectory.

Control: the gate requires an explicit closed artifact class and purpose. Its
authority is non-transitive; a broader or more linkable class needs a distinct
accepted evaluation.

### Stable pseudonyms or dates escape

Threat: HMAC stand-ins, exact dates or a mapping table allow linkage back to the
local source.

Control: the future gate requires source-independent synthetic identities,
relative/shifted dates and absence of local HMAC tokens, keys and mappings.
This tranche persists none of them and makes no anonymity claim.

## Residual risk

An explicit time token can still precede a header, note or composite entry; the
mapper therefore proves structural time attachment, not appointment semantics.
Rare trajectories may remain linkable even after direct identifiers are
removed. Both risks remain local and block automatic promotion. A separate
candidate-specific gate must decide whether minimisation and syntheticisation
are sufficient for the exact development use.

## Authority ceiling

This threat delta permits one synthetic-first mapper recovery and at most one
fresh bounded local content measurement. It grants no historical-derived
fixture/scenario/replay/corpus/memory use, provider/model transmission, product
runtime, database, ordinary-practice activation, production, deployment,
release, Pages, protected evidence or protected-ref movement.
