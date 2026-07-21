# Fresh Gemini veto: Reception One availability reconciliation

## Role and decision

Act as a fresh independent read-only veto reviewer. Return exactly one verdict:
`pass`, `revision_required`, or `blocked`. You own no implementation,
acceptance, integration, commit, push, protected-ref, baton, deployment or
release action. Do not edit any repository file.

## Exact workspace and lineage

- Review worktree:
  `C:\Users\sarashera\EMR4-worktrees\reception-one-availability-reconciliation-veto`
- Review branch: `antigravity/reception-one-availability-reconciliation-veto`
- Candidate: the exact clean `HEAD` checked out at launch; report its full SHA
- Source head: `e469fd60d37ab536152eda8e2cc4997431817110`
- Implementation branch: `codex/reception-one-availability-reconciliation`

Confirm branch, clean status and candidate head before reviewing. The candidate
must be a descendant of the named source head.

## Mandatory authority rehydration and read allowlist

Read only these paths and their source-to-candidate diff:

- complete `AGENTS.md`, especially Current Baton, Authority Allocation,
  Protected Evidence and Closed Gates, User Decision Boundaries, Ariadne rules
  and API Spine guardrails;
- `docs/bernie-reception-one-availability-reconciliation-plan.md`;
- `docs/security/bernie-reception-one-availability-reconciliation-threat-model-delta.md`;
- `orchestration/agent_inbox/codex/reception-one-availability-reconciliation-plan-sol-review.md`;
- `docs/diary/diary.html` and `docs/diary/meta-grid.js`;
- `docs/api-spine/async/integration-events.yaml` and
  `docs/api-spine/manifests/agent-capability-charters.yaml`;
- `scripts/reception_one_availability_reconciliation_harness.py` and
  `scripts/reception_one_availability_reconciliation_acceptance.py`;
- `tests/test_reception_one_availability_reconciliation.py` and the changed
  API Spine/meta-grid version guards;
- all files under
  `orchestration/prototypes/reception-one-availability-reconciliation/`;
- `orchestration/continuity/emr4-continuity-graph.json` and
  `orchestration/agent_inbox/codex/reception-one-availability-reconciliation-node.json`;
- receipt/runtime-state files beginning
  `reception-one-availability-reconciliation-` under
  `orchestration/agent_inbox/codex/`; and
- `orchestration/agent_inbox/codex/reception-one-availability-reconciliation-baseline-regression-comparison.md`.

The five authoritative sources are:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. State whether they reproduce before giving a verdict.

Do not open, enumerate, search, hash, infer from or otherwise inspect protected
holdouts or raw historical Diary material. Do not inspect `.env`, secrets,
credentials, tokens, unrelated local data, provider artifacts or anything
outside the allowlist.

## Mandatory review questions

1. Does the client treat `diary.appointment_rescheduled` only as a signal,
   require one exact scoped practitioner, freshly read the aggregate and exact
   availability, and avoid event-payload time as candidate truth?
2. Is canonical candidate identity independent of freshness-token churn, and
   does a surviving selection/proposal receive the fresh raw candidate while an
   occupied selection/proposal is cleared with no stale handoff?
3. When candidates materially change, can Back or interruption restore a stale
   selection/proposal, or are affected trail state, selected styling and
   proposal authority expired safely?
4. Do projection identity, close and interruption race guards prevent a slow
   reconciliation from overwriting newer user state?
5. Are other-practitioner, same-practitioner no-consequence, replayed,
   equal/older and failed-read cases silent without suppressing real candidate
   changes?
6. Are cues plain, nonmodal, patient-free in the live region, privacy-masked,
   keyboard safe and command-free, with dismiss, snooze, mute and review-context
   behavior matching the evidence?
7. Does the task-scoped Playwright runner use ordinary visible UI and real
   loopback FastAPI/PostgreSQL with no route interception, page-internal event
   invocation, browser appointment write, proposal handoff or confirmation?
8. Do evidence and hashes support all five viewports, exact combined scope,
   preserved then invalidated 3:30 state, Back, privacy, interruption, zero
   overflow, 44-pixel controls, clean console/network, two correlated support
   reschedules, replay, forced RLS, append-only rejection and exact cleanup?
9. Is the diff limited to the bounded client, declarative API Spine refinement,
   tests/evidence and Ariadne records, with no `app/`, Alembic, OpenAPI, API,
   database, event producer/schema, provider, PII, Stage 3B, voice, production,
   deployment or release expansion?
10. Is the Ariadne contract correctly left `gap` in the candidate pending this
    independent veto and later Sol acceptance, rather than self-granting
    authority?

A material freshness, stale-state, privacy, tenant, evidence-integrity or
authority defect vetoes acceptance.

## Permitted checks

You may run only read-only Git inspection, `node --check` for `meta-grid.js`,
Ruff over the two new Python scripts/test, and these serial pytest files using
`C:\Users\sarashera\emr4\.venv\Scripts\python.exe`:

- `tests/test_reception_one_availability_reconciliation.py`;
- `tests/test_reception_one_committed_event_client.py`; and
- `tests/test_api_spine_artifacts.py`.

Do not start or regenerate a browser, backend, database, migration, evidence or
cleanup run. Do not make any external/provider call beyond the selected
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

