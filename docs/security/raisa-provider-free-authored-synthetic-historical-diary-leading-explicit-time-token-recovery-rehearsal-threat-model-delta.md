# Raisa provider-free authored-synthetic historical Diary leading explicit time-token recovery rehearsal — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T07:45:30.6819253+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_threat_delta`

Operation: `raisa-provider-free-authored-synthetic-historical-diary-leading-explicit-time-token-recovery-rehearsal`

## Assets

- the closed parser grammar and same-segment mapping meaning;
- authored-synthetic positive and hostile cases;
- private normalized payload and ephemeral HMAC inputs;
- the unchanged coordinate-mapping fallback;
- the closed historical-derived first-use gate; and
- repository history, protected refs, `docs/branding/` and unrelated untracked
  files.

## Threats and controls

### A free embedded substring becomes scheduling time

Threat: a time-like sequence anywhere in a note, identifier or payload is
treated as the segment clock.

Control: matching is anchored at character zero after existing structural cell
segmentation and trimming. Nonleading and embedded examples are explicit
denials. The parser never searches forward for a token.

### An attached identifier passes as a complete token

Threat: a token prefix in an alphanumeric, digit continuation, phone number or
date is accepted.

Control: the complete time must be followed by one or more allowlisted ASCII
space, tab or hyphen separators and a non-empty payload. Attached characters,
invalid hours/minutes, date-shaped tails and phone/email-bearing payloads are
rejected with hostile authored-synthetic controls.

### Parser state invents time for later content

Threat: one admitted time is forward-filled across later segments, rows or
cells.

Control: the pure parser returns a value only for its current argument. The
projection loop has no retained leading-token clock. A subsequent segment must
carry its own valid token or independently satisfy the unchanged coordinate
mapper.

### The time token contaminates stable payload identity

Threat: including the recovered clock in normalized occupancy or HMAC input
makes identity depend on presentation syntax and preserves unnecessary source
detail.

Control: successful parsing removes the token and complete separator before
normalization, occupancy collection and HMAC token construction. Focused tests
compare the exact private token input/effect and fail if the clock survives.

### Direct parsing silently weakens coordinate controls

Threat: adding a direct mapping changes the accepted same-page distance or tie
rules for other segments.

Control: coordinate code and thresholds are unchanged. Direct mapping applies
only to the payload in the same successfully parsed segment; every other
segment follows the existing mapper and closed reason codes.

Candidate admission counts story anchors and valid leading tokens only as
explicit time-source observations. Distinct-minute, interval, mapping-ratio,
stable-linkage, adjacent-change and leakage controls remain separate; a high
token count cannot substitute for any of them.

### Authored-synthetic proof reopens private historical data

Threat: tests enumerate, import, open or tune against the ignored archive or a
consumed measurement attempt.

Control: the tranche uses constructed strings and in-memory typed extraction
objects only. No historical root or attempt is an input. Source-boundary tests
and review forbid filesystem enumeration or content-run entry points.

### Parser success is mistaken for first-use admission

Threat: a pure parser is described as proving a historical-derived scenario is
safe or useful.

Control: the result ceiling is a provider-free parser candidate only. No
historical derivative exists in this tranche and the first-use gate remains
default-deny until a later candidate-specific evaluation is useful.

## Residual risk

Authored-synthetic grammar coverage cannot prove that the historical documents
contain leading tokens or that any recovered payload represents an appointment
rather than a break, roster note or other operational text. A later fresh
local measurement may still find zero admissible tokens. Even a positive count
will not establish anonymity, product suitability or first-use admission.

## Authority ceiling

This delta permits one pure parser, one existing in-memory projection seam and
authored-synthetic tests. It grants no historical enumeration or access, no
reusable historical-derived artifact, no provider/model transmission, no
product/runtime/database use, no ordinary-practice activation, no first-use
admission, and no production, deployment, release, Pages, protected evidence
or protected-ref movement.
