# DeepSeek Sprint R3 Backend Stale Session Hardening — Implementation Plan

| Item | Value |
|---|---|
| Role | codex-worker |
| Worker Name | Shen-2 / DeepSeek Flash |
| Worker Branch | `codex/sprint-r3-deepseek-backend-hardening` |
| Status | plan_gate — not yet implemented |

## Protocol Status

| Item | Value |
|---|---|
| `handin` | Unable to run: `python` is not on PATH. Read AGENTS.md, protocol_alerts.md, parallel_workstreams.md, and task packet manually. |
| `git status` | Clean tracked code on branch `codex/sprint-r3-deepseek-backend-hardening` |
| `git branch` | `codex/sprint-r3-deepseek-backend-hardening` |
| Python availability | Not found via `python`, `py`, or `python3`. `.venv` not present. Cannot run `agent_worktrees.py` commands. |
| Plan approach | Manual plan artifact written to `orchestration/agent_inbox/codex/plan-deepseek-sprint-r3-backend-hardening.md` |

## My Understanding

The Bernie session store (`InMemoryBernieSessionStore`) is the server-owned state-machine for booking sessions. Clients (diary UI) send typed events with an `expected_revision` field — the session revision they last saw. When the actual session revision has advanced beyond that, the client has stale context. The store already rejects stale revisions (`stale_session_revision`), future revisions (`future_session_revision`), and conflicting idempotency keys for both client events and server outcomes. The route layer (in `app/routers/appointments.py`) also returns HTTP 409 for stale events and blocks confirm when `stale_reason_code` is set or freshness IDs mismatch.

**The core fail-closed stale session/revision guards are already implemented.** No production code change is needed for:
- Session revision staleness rejection (store + route)
- Idempotency conflict detection (client events + server outcomes)
- Freshness ID staleness gates (candidate + proposal at confirm)
- Session staleness blocking via `stale_reason_code` at confirm
- Diary-navigated and refresh-requested causing staleness

## Intended Surface / Boundary

### Affected surfaces
- **Bernie session store** (`app/services/bernie/session_store.py`): Already fail-closed. No production changes needed.
- **Bernie session/confirm route** (`app/routers/appointments.py`): Already fail-closed. No production changes needed.
- **Bernie turn evidence** (`app/services/bernie_turn_evidence.py`): Already fail-closed. No production changes needed.
- **Test files** (`tests/test_bernie_session_store.py`, `tests/test_bernie_session_routes.py`, `tests/test_bernie_confirm_create_proposal.py`): Existing coverage is solid but has scenario-level gaps that focused regression tests can fill.

### Surfaces that must NOT change
- **Diary UI** (`docs/diary/`): No changes.
- **Taskpane/Word add-in** (`EMR4 Sidebar/`): No changes.
- **GitHub Pages assets**: No changes.
- **Other appointment routes** (staff create, update, status, delete): No changes.
- **Gemini/Vertex provider**: No changes.
- **Persisted session table**: No changes — the in-memory store is deliberate.
- **Clarification merge flow** (Sprint R2): Must be preserved.
- **Patient collision source hardening**: No changes unless directly needed for stale-session safety.

## Out of Scope

- Live Gemini/Vertex calls
- Diary UI/pane/panel redesign
- Taskpane / Word changes
- GitHub Pages deployment
- GraphRAG/MCP/indexer automation
- Persisted session table redesign
- Broad patient collision source hardening
- AI provider boundary changes
- Headless agent driver / sprint infrastructure
- Any surface named by "cards", "slots", "stacking", "panels", "waiting room", "diary grid", "booking slot", or "status" that is not test-only regression coverage

## Files I Expect To Edit

Given no production gap, the only files that may change are:
- `tests/test_bernie_session_store.py` — Add focused stale-revision scenario tests (optional; existing coverage is strong)
- `tests/test_bernie_session_routes.py` — Add route-level stale confirm/status scenario tests (optional)
- `tests/test_bernie_confirm_create_proposal.py` — Add integrated stale-session confirm scenario tests with explicit stale freshness IDs (highest value)

If Claude's concurrent lane already covers these, this lane reports **no-code-needed**.

## Implementation Steps

### Step 0 — Assess Claude concurrent coverage
Before writing any test, check whether Claude has already submitted stale-session tests on its workstream. If so, skip.

### Step 1 — Focused regression tests (only if gaps remain after Step 0)
Add 2–3 targeted tests that prove existing production guards work at the integrated scenario level:

1. **Stale session confirm block** — Create a session, advance through staff_instruction ? interpretation ? slot_search ? candidate_selection ? proposal_preview, then manually set the session stale via `diary_navigated` refresh (or simulate stale session binding), and confirm that `confirm-bernie` returns blocked with `session_binding_stale_session` and writes no appointment/audit rows.

2. **Stale candidate freshness ID** — Submit confirm with a tampered/non-matching `candidate_freshness_id` and verify the endpoint returns blocked with `stale_candidate_freshness_id` and writes nothing.

3. **Stale proposal freshness ID** — Same for proposal freshness ID.

4. **Post-confirm stale event** — From a terminal confirmed session, send a stale `staff_instruction` with old revision and verify it gets `event_not_allowed_in_state` (not stale revision — the state machine already prevents this).

### Step 2 — Verify
- `py_compile` on all touched test files
- Focused pytest: `tests/test_bernie_session_store.py`, `tests/test_bernie_session_routes.py`, `tests/test_bernie_confirm_create_proposal.py`
- No regression in full Bernie suite
- `git diff --check`

### Step 3 — Submit plan
Record findings, verdict, and completion notes for Codex.

## Visual / Behavioural Acceptance Checks

No visual changes. All changes are backend test-only.

- `GET /api/v1/appointments/bernie/sessions/active` still returns `revision=0` for a fresh session
- `POST /bernie/sessions/{id}/events` with stale revision returns 409 and does NOT advance revision
- `POST /api/v1/appointments/proposals/create/confirm-bernie` with stale session binding blocks with `session_binding_stale_session`
- `POST .../confirm-bernie` with stale candidate/proposal freshness ID returns blocked with appropriate code
- No appointment or audit log rows are written for any stale path
- Fresh clarification flow from Sprint R2 still passes end-to-end

## Risks / Ambiguities

- **Claude overlap**: Claude's parallel stale-session hardening lane may already cover the same test gaps. If so, this lane should submit "no-code-needed" with analysis evidence rather than duplicate work.
- **Python unavailability**: Cannot run `agent_worktrees.py plan/submit` commands. Will create artifacts manually and report this constraint.
- **In-memory store**: All staleness guards are in-memory. A future persisted session table may need different staleness semantics.
- **confirm_submitted staleness**: The confirm endpoint calls `append_client_event(..., expected_revision=binding_revision, event_type=confirm_submitted, ...)` at line 6754. The `binding_revision` comes from the session binding built at the start of the confirm function. Between the session binding and the append call, the revision cannot advance because the store is single-threaded. No gap here.
- **Server outcome staleness**: Server outcomes arrive from the Bernie interpret/outcome handler, not from a client tab. The expected_revision for server outcomes is set by the server itself, so staleness there is a server-side/internal issue, not a client stale-context issue.

