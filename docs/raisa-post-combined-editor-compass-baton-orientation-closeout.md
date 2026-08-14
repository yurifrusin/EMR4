# Post-combined-editor Compass and baton orientation closeout

Date: 2026-08-15

Timestamp: 2026-08-15T06:42:00+10:00 (Australia/Brisbane)

Status: accepted; programme paused at a genuine Yuri-owned fork

Accepted reviewed source: `2ca3a111d2ee9277571ea3c905f22ce78c8e9745`

Result: `raisa_post_combined_editor_compass_baton_orientation_pass`

## Lay summary

Reception One has completed its first coherent command set: staff can change an
appointment's status, doctor, time and duration through backend-owned proposal,
confirmation and fresh-truth paths. There is no further high-value feature that
can honestly be selected from existing authority alone.

The recommended next direction is appointment cancellation. Its safe first
step is not a fifth button or a destructive write. It is a provider-free,
read-only review of the existing cancellation command path, especially the
ordinary Diary's delete-to-status compatibility fallback. That review would
decide whether one existing family can be reused unchanged or whether a small
convergence repair must precede any Reception One control.

The patient-channel direction remains important but is a distinct programme
choice. A future email, SMS or Siri-like client would act as a separately
identified delegate under narrow, expiring authority. That authority can be
revoked at any time for future acts, including an uncommitted confirmation. It
does not silently erase an appointment that already committed; cancellation or
rescheduling requires its own newly authorised command and current-truth check.

## Technical result

The review found:

- exactly four Reception One controls: status, time, duration and practitioner;
- a complete status command family and one shared update command family;
- a presentation-only cancellation candidate with no operational Reception One
  bridge;
- distinct API Spine delete proposal/confirm operations;
- an ordinary Diary 404 fallback from delete proposal to `Cancelled` status
  proposal which omits `cancellation_reason`; and
- a confirm adapter able to dispatch either the delete- or status-family
  confirmation endpoint with its matching idempotency derivation.

This is not a vulnerability finding. It is an unresolved semantic seam that
must be understood before a second renderer exposes destructive behavior.

Candidate directions were classified as follows: cancellation, check-in,
patient-channel delegation and another event family require a Yuri decision;
Stage 3B requires participant action; operational durable-cue or restart work
remains authority-closed; visual polish is presently lower leverage.

## Evidence and verification

- Eight focused orientation assertions passed.
- The independent exact-candidate packet passed all 115 tests plus Ruff and Git
  whitespace checks.
- The canonical fast profile passed Ruff, compilation of 209 maintained Python
  sources, 196 tests, Diary JavaScript syntax and Git whitespace checks.
- Gemini 3.6 Flash/high independently cleared all ten required challenges at an
  unchanged clean candidate.
- The complete correction-register suite passed after AER-0320 recorded and
  corrected a rejected pre-verifier receipt before any external call.
- The non-PHI Pushover closeout notification succeeded with request
  `2b495e4c-7e69-453a-919f-ad5fc9d5565c` and status `1`.
- Evidence label: `repository_static_authored_synthetic`.

## Parallelism efficacy

- DeepSeek was declined because there was no stable mechanical implementation
  package.
- Native subagents were declined because successor selection was tightly
  coupled programme judgment.
- Gemini supplied the useful independent veto and had positive leverage.
- Sol retained evidence reconciliation, authority, continuity and Git control.

## Recommendation and pause

Ask Yuri whether to pursue Reception One appointment cancellation next,
beginning with the bounded provider-free read-only cancellation command-path
readiness review. Do not implement cancellation, add a control or modify a
command family until that choice is recorded.

Retained alternatives are the patient-channel identity/delegation programme,
check-in/waiting-area work, representative Stage 3B sessions, another explicitly
chosen event family and later operational durability work.

## Claim boundary

No product, API, OpenAPI, GraphQL, database, event, watcher, channel, identity,
delegation, provider or runtime source changed. No patient/product/clinical
data, credentials, IAM, deployment, production, release, Pages or protected-ref
authority was opened.

Yuri attention required: yes.
