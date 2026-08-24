# Raisa local-only historical-derived minimised check-in-context scenario first-use materialisation rehearsal — threat-model delta

Date: 2026-08-24

Timestamp: 2026-08-24T11:28:39.9415173+10:00 (Australia/Brisbane)

Status: `frozen_one_run_no_retry`

## Change under review

One local process may read the already bounded dense-day Word snapshots and
write one ignored structural JSON fixture after exact candidate-gate admission.
This is the first historical-derived reusable artifact; its write and evidence
boundaries therefore fail closed independently of the source parser.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Private content reaches another agent/provider | GPT Sol owns one local serial run; no external lane, network, prompt, clipboard or telemetry surface is allowed. |
| An old private attempt is reused | New exact attempt and fixture roots must be absent; the bind selects directly from the exact source root. |
| Scope expands beyond one day/80 files | Non-recursive exact-root binder enforces one dense day, 80 files, per-file and total-byte caps, metadata drift and reparse denial. |
| Word executes active content | Invisible Word, alerts off, macros forced disabled, link updates disabled and documents read-only remain mandatory. |
| Raw text or identifying coordinates enter the fixture | The writer accepts only the gate's closed numeric/event model; source text, tokens, dates, filenames, paths, coordinates, keys and mappings are unrepresentable. |
| Random tokens become durable pseudonyms | Tokens exist only in the in-memory projection; persisted slots are small ephemeral ordinals and no slot mapping is written. |
| A broad replay is disguised as a scenario | The gate requires 3–12 events, a 10–120-minute span, at least three minutes and two kinds, and limited subject/resource slots; whole-day replay blocks. |
| Candidate changes after admission | Digest is computed over canonical bytes; the exact admitted digest must equal the temporary file and final file digest. |
| A block or partial failure leaves a fixture | Non-admission and exceptions remove exact owned temporary/output files; one-file root postcondition is mandatory for success. |
| Writer cleanup deletes unrelated data | Cleanup resolves and verifies the exact two owned roots under the ignored historical-trove parent; no broad glob or recursive workspace operation is permitted. |
| Word process survives failure | The existing exact child-PID control and parent cleanup receipt remain mandatory; unrelated Word processes are preserved. |
| A rerun normalizes an unsafe failure | Bind and content terminals are single-use; no retry or fallback is authorised in this tranche. |
| Sanitized evidence overclaims privacy | Evidence records only this fixture's zero-forbidden-field reading and absence checks; it makes no universal reconstruction or de-identification claim. |

## Residual boundary

An admitted fixture is suitable only for local provider-free development tests.
It is not source truth, product data, a patient record, practice validation,
ordinary-practice authority, model memory, training data or production input.
