# Reception One duration DeepSeek test integration recovery

Date: 2026-08-14

Timestamp: 2026-08-14T11:42:56+10:00 (Australia/Brisbane)

Status: `sol_recovery_complete_candidate_pending_independent_veto`

Worker source: `f08a16960c26f400954fbfedc3e30ff2b87705c6`

Integration commit: `52ee727928f32581f5fd5a969bfbcde55a13d87d`

## Preserved worker result

DeepSeek V4 Flash/high produced exactly one new isolated artifact,
`review/test_reception_one_duration_action.py`, in its assigned clean worktree.
It did not edit product source, execute pytest, claim acceptance, push a ref or
touch a protected surface. Its terminal receipt is preserved at
`orchestration/agent_inbox/deepseek/raisa-reception-one-duration-test-worker-receipt.json`.

The pre-implementation candidate correctly targeted a paired six-outcome
route-intercepted browser matrix, exact proposal/confirm counts, immutable
appointment fields, zero raw writes, focus/Escape behavior and responsive
containment. It was useful source, but not transferable acceptance evidence.

## Admission finding

The candidate assumed a free-form numeric duration input, a
`duration-input` test id and a `changeAppointmentDuration` bridge name. The
frozen plan instead requires a bounded selector whose options are derived from
the exact current duration in whole 15-minute deltas while preserving valid
non-multiple-of-15 current durations. Those assumptions were therefore not
admitted unchanged.

This is ordinary untrusted-candidate recovery under the orchestrator recovery
lease, not a qualifying agent-error-register incident: the worker stayed
inside its packet, labelled the artifact expected-red, made no acceptance
claim and supplied a complete terminal receipt.

## Sol amendments

Sol retained the test's useful paired-outcome structure and amended it to:

1. drive the frozen `New duration` bounded selector and
   `meta-grid-duration-select` contract;
2. use the implemented `resizeAppointmentDuration` bridge and exact
   `metaGridResizeAppointmentDuration` static boundary;
3. test closed invalid/no-op/out-of-day targets as zero-route denials rather
   than injecting invalid values into the visible UI;
4. preserve the exact fresh appointment read as the sole source of displayed
   duration/end truth; and
5. keep the worker artifact self-contained and route-intercepted, with no
   live-backend or database claim.

Executing the recovered matrix exposed a real product defect that the original
shape was intended to challenge: the ordinary Diary callback could announce a
terminal committed state before the duration bridge completed its mandatory
exact fresh read and projection update. The bridge now suppresses terminal
callback phases until that reconciliation succeeds. A subsequent rendered
phone check exposed one newly composed mojibake en dash; the source now uses
the correct Unicode range separator.

## Verification

- The recovered duration matrix, time/status regressions and two-projection
  truth-parity packet pass as part of the consolidated 118-test run.
- The affected Diary/UI packet is included in that same 118-test run.
- The canonical fast profile passes 196/196, including Ruff, maintained-source
  compilation, JavaScript syntax and Git whitespace.
- In-app browser inspection passes at 1280x900, 768x1024 and 390x844 with no
  horizontal overflow, a visible bounded selector, duration-specific review
  dialog, Escape cancellation and focus return to the selector.

The recovered source remains pending one fresh Gemini 3.6 Flash/high
independent veto. Sol alone retains acceptance, integration and baton
authority.

## Boundary

This recovery adds no backend, API, OpenAPI, GraphQL, database, event, watcher,
provider, product/patient data, deployment, release, Pages or protected-ref
authority. It preserves `docs/branding/` and every unrelated untracked file.
