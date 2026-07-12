# S5 D2 — Backend Contract & API Audit

| Field | Value |
|---|---|
| Lane | D-2 |
| Sprint | S5 |
| Role | `deepseek-flash-workers` (instance 2) |
| Model | `deepseek-v4-flash` / high |
| To | DeepSeek (Deep Code) |
| Packet | `orchestration/agent_inbox/deepcode/deepcode-s5-d2-backend-contract-audit.md` |
| Completion artifact | `orchestration/agent_inbox/codex/review-deepcode-s5-backend-audit.md` |
| Status | dispatched |
| Date | 2026-07-11 |
| Parent plan | `plan-claude-fable-emr4-receptionist-workflow-audit.md` |

## Handin

Run these in your worktree **before starting**:

```powershell
python scripts\agent_worktrees.py handin --agent deepcode
python scripts\agent_worktrees.py sync --fetch
```

Then read the protocol alerts printed by `handin`. Trust those alerts over any remembered process details from prior sessions.

## Authority

You are DeepSeek worker lane **D-2**. Own only:

- Read-only audit: `app/routers/appointments*.py`, `app/routers/diary.py`, `app/schemas/appointments.py`, `tests/`, `review/`
- **Failing-test proposals only** — you may write test files that document a discovered defect, but must not write production code
- Your completion artifact at `orchestration/agent_inbox/codex/review-deepcode-s5-backend-audit.md`

**Do not** edit production code beyond failing-test proposals (in `tests/` or `review/` only). Do not commit, push, run commands on other agents, claim integration authority, or touch `master`/`handoff/current`.

## Mission

Audit the **backend contracts, conflict/slot logic, and API surface** that the receptionist appointment workflow relies on — against the local dev stack (Postgres + uvicorn, seeded dummy data, `dr.shera@emr4dev.local` only).

### 1. Contract audit

Review these API routes for correctness against their schemas:

- **Appointment CRUD**: `app/routers/appointments*.py`
  - `GET /api/v1/appointments` — date filtering, practice scoping, auth gating
  - `POST /api/v1/appointments` — creation payload, conflict detection, status defaults
  - `PUT /api/v1/appointments/{id}` — update mutation, status transition rules
  - `DELETE /api/v1/appointments/{id}` — cancellation/deletion rules
- **Slots**: `GET /api/v1/appointments/slots` — duration-aware slot calculation, practitioner/date scoping, conflict avoidance
- **Proposal**: `POST /api/v1/appointments/proposals/create` — booking proposal command, non-mutating validation
- **Diary template**: `GET /api/v1/diary/template` — practice template or JSON fallback

### 2. Conflict & validation audit

- Verify appointment conflict detection: overlapping times with same practitioner
- Verify adjacent booking allowances (Cancelled/NoShow/DNA are non-blocking per existing tests)
- Verify duration-aware slot calculation returns correct available slots
- Verify proposal endpoint validates correctly without mutating

### 3. Auth & security gating

- Verify each endpoint returns 401 without a valid JWT
- Verify practice scoping (cross-practice isolation)
- Verify role gating where applicable

### 4. Evidence gathering

Run all existing tests and record results:

```
pytest tests -q
pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q
```

For any defect found: write a **failing test** (in `tests/` or `review/`) that documents the defect, with the assumption the fix will make it pass. Do not fix the production code — leave the failing test as evidence.

### 5. Schema & response shape audit

Verify response schemas match what the frontend expects:
- `appointment.status` lifecycle values match what diary.js renders
- `PractitionerBrief` includes `ahpra_number` for column mapping
- `AppointmentType` includes `color_hex`, `name`, `duration_minutes`
- Response pagination and date-range filtering work correctly

## Classification

Classify every finding as one of:

- **Material functional defect** — the API is broken, returns wrong data, crashes, or violates its schema
- **Material usability defect** — the API works but returns confusing or unnecessarily hard-to-consume data
- **Minor** — cosmetic, non-blocking, can be deferred
- **Observation** — not a defect but worth documenting for future reference

## Boundary

**In scope:**
- Backend API contracts and schemas (read/audit + failing-test proposals only)
- Existing test suite health
- Auth gating, practice scoping, role gating
- Conflict detection, slot calculation
- Schema/response shape correctness

**Out of scope (stop conditions — do not propose, plan, or code anything in these areas):**
- No production code edits beyond failing-test proposals
- No Bernie D5; no provider/live-provider wiring; no memory/RAG/GraphRAG
- No historical diary trove or H15/H-series runtime imports
- No new write authority, no new mutating endpoints, no schema migrations
- No deployment/production readiness changes
- No GraphQL, external clients, or Pages changes
- No real PHI or `local_data` — use only dev dummy data

## Completion

Write your completion artifact at `orchestration/agent_inbox/codex/review-deepcode-s5-backend-audit.md`.

## Completion Notes (filled by worker)

### Files changed
- `orchestration/agent_inbox/codex/review-deepcode-s5-backend-audit.md` (created — audit artifact, DECISION: pass)
- `review/test_raw_status_terminal_rollback_guard.py` (created — failing-test proposal for terminal→non-terminal status rollback)

### Verification
Static code review completed. pytest could not be executed from this Deep Code session (non-TTY constraints).

### Remaining risks
- Terminal-status rollback gap on raw PATCH status endpoint (documented via failing-test proposal)
- No pagination on GET /appointments (scale issue)
- Raw-compat PUT allows mutation of terminal appointments

The artifact must begin with `DECISION: pass` or `DECISION: revision_required`. Include:
- Contract-by-contract audit results
- Each finding classified (material functional defect / material usability defect / minor / observation)
- Reproduction steps or request/response transcripts for any defect
- Names of any failing-test files written
- `pytest tests -q` result
- `pytest review/test_diary_smoke.py` result
- Explicit statement that no commands, commits, pushes, or out-of-scope writes occurred beyond this packet

Submit via:

```powershell
python scripts\agent_worktrees.py submit --agent deepcode --task deepcode-s5-d2-backend-contract-audit --commit-message "S5 D2 backend contract audit findings" --message "DeepSeek S5 D2 backend audit ready for Codex review"
```
