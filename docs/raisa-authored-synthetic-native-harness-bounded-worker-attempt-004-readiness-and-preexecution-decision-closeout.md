# Attempt-004 Readiness and Preexecution Decision Closeout

Date: 2026-08-21
Timestamp: 2026-08-21T11:59:13.0977106+10:00
Status: `accepted`

Result:
`ready_for_one_separately_checkpointed_occupied_attempt_004`

Exact implementation source:
`0ef8ab1317e21152c9ee7c331801183250361745`

Pre-verifier acceptance binding:
`a96448a17bcb14753042a20f277fbd7e954e78e4`

## Lay summary

The fourth DeepSeek Harness attempt is ready to be tried once, but it has not
been started yet. The test checked the whole chain around it: a new identity,
the exact Harness package and preset, the small synthetic coding task, the
broker limits, the clock connection, the diagnostic record and cleanup. The
three earlier attempts cannot be reused.

The current clock reading was deliberately only a readiness reading. The real
attempt must take a fresh reading after this closeout, preventing an old lease
or work order from being carried forward by hand. If the next checkpoint is
valid, exactly one run is allowed. There is no automatic retry or fallback.

## Technical result

- exact rc.7 `@deepseek-ai/dsh` package identity and materialized source: passed;
- `emr4-bounded-worker`, `headless`, `deepseek-v4-flash`/high and exact ordered
  `edit`, `glob`, `read` view: digest-bound;
- baseline authored-synthetic task and expected one-file edit: digest-bound;
- broker and closed v2 work-order schema: digest-bound;
- attempts 001-003: seven accepted artifacts byte-identical, all attempt
  identities consumed, non-resumable and zero-retry;
- attempt 004: disjoint operation/attempt/work-order/lease identity, exact
  disposable root absent and twelve future evidence paths absent;
- diagnostic selection: canonical exact identity selects v2; absent or invalid
  evidence fails closed with its reason; terminal write precedes cleanup;
- readiness clock: generation `gen-ffb51b2915d8a99ef85f7a10d61d881ed2d7ea1f6df6e936ab66504dabc8e7a0`,
  lease sequence 103, read-only and non-reusable;
- focused verification: `32/32` passed; Ruff, compilation, schema and diff
  hygiene passed;
- Node / Harness / broker / worker / session / prompt / tool / model / provider
  / network actions: all zero.

The future occupied envelope is one native process, one session, one turn, at
most one provider request, at most one model tool call, 4,096 output tokens,
300-second upstream timeout, 420-second native deadline, and zero retry,
resume, fallback or second worker.

## Parallelism result

- DeepSeek: `not_applicable`; readiness could not execute the model it governs.
- Gemini: `not_applicable`; exact local identity, schema, hash, clock and cleanup
  evidence supplied the bounded decision.
- Native subagents: `declined`; developer policy and one serial identity/lease
  seam admitted no delegated package.

No worker or verifier agent was launched.

## Workflow controls

AER-0756 records the first preplanning receipt's fail-closed rejection of one
manually supplied full protected-ref object in the prose evidence field. The
preserved rejected receipt proves the machine-binding rule worked before any
planning write. The corrected receipt contains zero caller-supplied Git object
IDs and passed all five sources.

AER-0757 records the successor rehydration's discovery that several documents
in the preceding accepted repair had `Date:` but no required Brisbane
`Timestamp:`. Accepted historical evidence remains immutable. This tranche adds
a focused test requiring both fields and the explicit `+10:00` offset in every
new plan and threat delta; its closeout, Sol acceptance and Yuri summary also
carry the pair. The control converts a memory requirement into a reading.

AER-0758 records that the first closeout draft manually expanded the
pre-verifier commit abbreviation into an incorrect 40-character value. A
direct `git rev-parse` reading caught it before staging. Every closeout binding
now uses the machine-resolved object
`a96448a17bcb14753042a20f277fbd7e954e78e4`; no candidate or runtime effect
occurred.

AER-0759 records the first read-only clockwork check's rejection of the
descriptive node kind `rehearsal`, which the live Compass graph does not admit.
The readiness checker now uses the admitted `tooling` kind; rejection preceded
transaction preparation, command execution and publication.

## Boundaries and successor

This result does not authorize occupied execution from the readiness tranche.
It permits the clockwork closeout to establish the separately named attempt-004
operation. That successor must perform a fresh five-source rehydration, resolve
the full current candidate from Git, take a fresh post-closeout clockwork
checkpoint and then execute at most once.

`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`
remains exact. Product source/configuration, API, database, route, adapter,
generic-status `Arrived`, grammar, first-party client, waiting area, product or
patient data, clinical data, production, deployment, release, Pages and
protected refs remain closed.
