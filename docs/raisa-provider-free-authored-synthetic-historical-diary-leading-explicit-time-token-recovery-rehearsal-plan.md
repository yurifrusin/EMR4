# Raisa provider-free authored-synthetic historical Diary leading explicit time-token recovery rehearsal — plan

Date: 2026-08-24

Timestamp: 2026-08-24T07:45:30.6819253+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_plan`

Operation: `raisa-provider-free-authored-synthetic-historical-diary-leading-explicit-time-token-recovery-rehearsal`

Planning source HEAD: `05bef5dc9fc8f85a6ec6fd62c00d4e670d624912`

Reasoning level: High. The accepted successor contract already fixes the
position, token, separator, denial and authority meaning. This tranche lowers
that contract into one pure parser and one existing projection seam without
historical, provider, product or runtime access.

## Objective and inherited evidence

Implement and prove a strict segment-leading explicit time-token parser on
authored-synthetic values only.

The accepted historical measurement at exact reviewed source
`5df44bd28ae60db773b6fd833d0d8cdecca45611` completed all 80 bound snapshots
but found zero complete main-story time anchors. Earlier aggregate evidence
reported 78 whole-document time-like substrings, while a strict table-cell
whole-segment measurement also found zero complete tokens. The next narrow
hypothesis is therefore an explicit time token at the beginning of a table-cell
segment that also contains its payload. This tranche proves only the parser; it
does not reopen or enumerate the historical archive.

## Frozen parser contract

The implementation remains in
`orchestration_harness/historical_diary_local_measured_privacy_probe.py` and
operates on one already separated in-memory cell segment.

1. Existing structural cell splitting removes Word end-cell markers,
   normalizes paragraph boundaries and trims surrounding whitespace before the
   parser is called. The parser does not join segments or inspect neighbouring
   rows, cells or documents.
2. The token must begin at character zero of that trimmed segment. It uses the
   existing complete time semantics: `H:MM`, `HH:MM`, `H.MM` or `HH.MM`, with
   optional case-insensitive `am`/`pm`; hours, minutes and 12-hour suffixes
   retain their existing bounds.
3. A token must be followed by one or more ASCII spaces, tabs or hyphens and a
   non-empty payload. An attached letter, digit or other punctuation is not a
   separator. Unicode dash variants are not silently admitted.
4. A nonleading or embedded token is rejected. Invalid hours/minutes,
   digit-continuations, attached alphanumerics, date-shaped tails and payloads
   containing phone or email contact shapes are rejected.
5. On success the parser returns only the integer minute and the payload with
   the leading token and separator removed. The token never enters normalized
   payload occupancy or private HMAC token material.
6. The explicit minute applies only to that same segment. It is not retained as
   parser state and is never forward-filled to a later segment, row or cell.
7. A valid leading token is the direct time mapping for its own payload. The
   existing same-page coordinate mapper remains unchanged and is consulted only
   when the segment has no valid leading token. A standalone complete time
   segment remains a structural marker and does not become a payload.

The only new public mapping reason is a closed aggregate code such as
`leading_explicit_time_token`; no raw token, payload, time value, source text,
coordinate, path or identity may enter public output.

## Authored-synthetic proof matrix

Focused tests must cover:

- 24-hour boundaries (`00:00`, `9:05`, `09.05`, `23:59`) and valid 12-hour
  conversions including `12:00am` and `12:00pm`;
- ASCII space, tab and hyphen separators, mixed case suffixes and harmless
  surrounding structural whitespace;
- invalid hour/minute and invalid 12-hour combinations;
- attached letters, attached digits, slash/colon/punctuation continuations,
  missing payload and nonleading embedded tokens;
- date-like, phone-like and email/contact-like payload denials;
- same-segment direct mapping, no forward fill, unchanged coordinate fallback,
  and standalone time-marker behavior;
- byte-stable proof that the leading time and separator are absent from the
  private normalized payload/HMAC input; and
- strict zero filesystem enumeration, historical-content access, network,
  provider/model, product, database and client effects.

The complete existing historical-Diary provider-free suite must still pass.
Ruff, compileall, source-boundary scans, JSON validation and `git diff --check`
must pass. No historical file is needed or permitted for any test.

## Acceptance and recovery

`accepted_parser_recovery_candidate` requires every positive authored-synthetic
case, hostile rejection, integration assertion and existing provider-free
control to pass with zero historical access and zero source-value leakage.

`revision_required` applies to a contained semantic or integration gap that
does not access historical data. A single narrow mechanical correction may be
made under Sol ownership and the complete provider-free suite rerun.
`blocked` applies to historical access, unbounded matching, raw-value output,
contact/date admission, forward fill, token-in-hash evidence, provider/product
activity, or an unresolved deterministic failure.

The strongest result is a provider-free parser candidate for a separately
planned fresh local historical measurement. It is not historical evidence, an
anonymity claim, a reusable historical-derived scenario or first-use admission.

## First-use gate

The first-use gate remains `closed_pending_candidate_specific_evaluation`.
Wholly authored-synthetic parser cases do not require that gate because they
contain no historical derivative. This tranche creates no historical-derived
fixture, scenario, benchmark, replay, corpus, memory/RAG input or product test.
If a later fresh local measurement produces a useful minimized candidate, that
particular derivative must be evaluated before its first reusable development
use.

## Parallelism assessment

- **DeepSeek:** declined with negative leverage. The native Harness remains
  paused from occupied EMR4 use, Claude Code is not an authorised silent
  fallback, and packet/recovery cost exceeds this one-parser seam.
- **Gemini:** not applicable with neutral leverage. The proof is deterministic,
  provider-free and does not require an external veto call.
- **Native subagents:** declined with negative leverage. Parser semantics,
  HMAC-input stripping and the projection tests are one tightly coupled change
  whose briefing and reconciliation cost exceeds its separable work.
- **GPT Sol:** owns the frozen parser, hostile matrix, integration, complete
  provider-free verification, acceptance, Git and closeout.

Reassess on deterministic failure, before any worker dispatch, and at the next
named tranche boundary.

## Closed surfaces

No historical archive enumeration, metadata/content access, prior-attempt
reuse or retry; no source text, filename, timestamp, path, identity, note,
contact value, raw time token, coordinate, key or mapping release; no provider,
network or model; no product runtime, route, API, client, database or
configuration; no ordinary-practice activation; no first-use admission; and no
production, deployment, release, Pages, protected evidence or protected-ref
movement. Local/origin `master` and `handoff/current` remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and
all unrelated untracked files. Stage explicit paths only.
