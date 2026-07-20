# Fresh Gemini veto: Reception One committed-event vertical

## Role and decision

Act as a fresh independent read-only veto reviewer. Return exactly one verdict:
`pass`, `revision_required`, or `blocked`. You own no implementation,
acceptance, integration, commit, push, protected-ref, baton, deployment or
release action. Do not edit any repository file.

## Exact workspace and lineage

- Review worktree: `C:\Users\sarashera\EMR4-worktrees\reception-one-committed-event-veto`
- Review branch: `antigravity/reception-one-committed-event-veto`
- Candidate: the exact clean `HEAD` checked out at launch; report its full SHA
- Source head: `be5e01d00b23ef43f7aab8b30f6dbdfa6e858c45`
- Implementation branch that supplied the candidate:
  `codex/reception-one-committed-event-vertical`

Confirm the branch, clean status and candidate head before reviewing. The
candidate must be a descendant of the named source head.

## Mandatory authority rehydration and read allowlist

Read only these paths and the source-to-candidate diff over them:

- complete `AGENTS.md`, especially Current Baton, Authority Allocation,
  Protected Evidence and Closed Gates, User Decision Boundaries, Ariadne rules
  and API Spine guardrails;
- `docs/bernie-reception-one-committed-event-vertical-plan.md`;
- `docs/security/bernie-reception-one-committed-event-threat-model-delta.md`;
- `orchestration/agent_inbox/codex/reception-one-committed-event-vertical-plan-sol-review.md`;
- new/changed application and migration files under `app/` and the exact new
  migration `alembic/versions/n3o4p5q6r7s8_add_reception_one_committed_events.py`;
- `docs/api-spine/async/integration-events.yaml`,
  `docs/api-spine/manifests/agent-capability-charters.yaml`, and
  `docs/api-spine/openapi/diary-committed-events.yaml`;
- `docs/diary/diary.html`, `diary.js`, `meta-grid.js`, `meta-grid.css` and
  `office-bootstrap.js`;
- `scripts/reception_one_committed_event_harness.py` and
  `scripts/reception_one_committed_event_acceptance.py`;
- `tests/test_reception_one_committed_event_runtime.py`,
  `tests/test_reception_one_committed_event_client.py`,
  `tests/test_reception_one_committed_event_evidence.py`, and the changed
  meta-grid/API Spine guard tests;
- JSON and screenshots under
  `orchestration/prototypes/reception-one-committed-event-vertical/`; and
- the Ariadne receipt/runtime-state files whose names begin
  `reception-one-committed-event-vertical-` under
  `orchestration/agent_inbox/codex/`.

The five authoritative sources are:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. State whether they reproduce before giving a verdict.

Do not open, enumerate, search, hash, infer from, or otherwise inspect protected
holdouts or raw historical Diary material. Do not inspect `.env`, secrets,
credentials, tokens, unrelated local data, provider artifacts or anything
outside the allowlist.

## Mandatory review questions

1. Does only the existing signed appointment-update confirmation produce the
   one authorised `diary.appointment_rescheduled` event, and only for an actual
   start/duration change while the feature is enabled?
2. Do appointment truth, update audit, idempotency completion and event append
   share one transaction, with retry deduplication and injected-failure rollback
   leaving no split state?
3. Do database constraints enforce the exact patient-free payload allowlist,
   correlation, practice-qualified appointment/command/audit links, uniqueness,
   24-hour eligibility, forced RLS and rejection of event UPDATE/DELETE?
4. Is the feed authenticated, practice scoped, read-only, batch bounded and
   default-off, with a signed practice-bound opaque cursor that avoids both
   historical disclosure and loss of the first later event from empty history?
5. Does the browser treat an event only as a signal, require active-projection
   membership, perform a fresh exact appointment read plus the exact current
   projection read, and suppress irrelevant, stale, replayed, superseded or
   failed-read cases?
6. Are attention effects nonmodal, bounded and memory-only, with no autofocus,
   speech, persistence or command tunnel, and do dismiss, snooze, mute,
   show-context, Escape focus restoration and privacy masking behave as claimed?
7. Does the real Playwright evidence drive ordinary visible UI with no
   `page.route` or mocked transport, and do five viewports, keyboard,
   interruption, zero overflow, 44-pixel controls and clean console/network
   evidence genuinely reproduce?
8. Does PostgreSQL readback prove exactly two synthetic reschedules and their
   command/audit/event correlations, one idempotent replay, unrelated-event
   suppression, forced-RLS isolation, append-only rejection and exact cleanup?
9. Do GraphQL mutations/subscriptions, new appointment commands, other event
   families, providers, PII, protected/historical evidence, Stage 3B, voice,
   external transport, background workers, production, deployment and release
   remain closed?
10. Are all claims calibrated to `authored_synthetic_local`,
    `live_local_backend_postgres`, or
    `live_local_browser_backend_postgres`, with no production, representative
    usability or provider claim?

A material transaction, tenant, privacy, freshness, deduplication, evidence or
authority defect vetoes acceptance.

## Permitted checks

You may run only read-only Git inspection, Node syntax checks, Ruff, and the
three focused committed-event pytest files using
`C:\Users\sarashera\emr4\.venv\Scripts\python.exe`. Pytest must be serial.
Do not start or regenerate a browser, backend, database, migration, evidence or
cleanup run. Do not make any external/provider call beyond the already selected
Antigravity review transport.

## Required output

Return one concise Markdown report containing:

- `Verdict: pass | revision_required | blocked`;
- exact candidate head and clean-worktree confirmation;
- material findings first, with file/line or artifact evidence;
- explicit answers to all ten questions;
- supplied-versus-rerun check results;
- residual risks and claims not made; and
- one-sentence recommendation to Sol.

If there is no material finding, say so explicitly.
