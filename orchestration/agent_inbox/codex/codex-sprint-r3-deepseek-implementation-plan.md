# Implementation Plan: DeepSeek Stale Session Revision/Context Regression Lane

| Item | Value |
|---|---|
| **Agent** | codex (DeepSeek Flash via codex-deepseek-bridge) |
| **Branch** | `codex/sprint-r3-deepseek-stale-session-regression` |
| **Dispatched at** | `f8bc6c8` (Dispatch Sprint R3 stale session hardening) |
| **Role** | codex-worker (regression lane) |

---

## My Understanding

Sprint R3 hardens stale-session and stale-revision guards across the Bernie booking session stack. The existing R2 work built:
- `InMemoryBernieSessionStore` with strict revision ordering, idempotency, and PHI payload guardrails (`app/services/bernie/session_store.py`)
- HTTP session routes (`/api/v1/appointments/bernie/sessions`) with stale-revision 409 rejection, cross-owner rejection, and PHI guard (`app/routers/appointments.py`)
- `check_staleness()` in `bernie_turn_evidence.py` for freshness-id and reference-date staleness gates at the confirmation endpoint
- `BernieReceptionContextFrameSet` / `BernieStaleEvidenceFrame` as typed frame contracts evaluated by `evaluate_reception_context()` in `app/services/bernie/policy.py`

Existing R2 test coverage includes:
- **`test_bernie_session_store.py`**: stale revision rejection, future revision rejection, idempotency, cross-owner/wrong-surface, PHI guard, server-outcome ordering, proposal binding
- **`test_bernie_session_routes.py`**: HTTP-level stale revision (409), idempotent replay, conflict, cross-user, wrong-surface, PHI guard
- **`test_bernie_clarification_merge.py`**: Two-turn clarification field carry-forward (patient, practitioner, date, time, duration), new-reply-wins, no DB writes
- **`test_bernie_confirmed_flow_review_harness.py`**: Full normalize→search→select→confirm, no AI provider calls, row-count assertions
- **`test_bernie_context_frames.py`**: `BernieStaleEvidenceFrame` blocks confirmation without becoming no-slot
- **`test_deepseek_clarification_regression.py`**: Slot normalizer invariants, replay harness integrity, clarification fixture structure
- **YAML scenario fixtures**: `refresh_does_not_resurrect_stale_latest_message`, `confirm_required_before_create_or_update`, clarification merge fixtures

This regression lane independently reviews/tests the **gaps between existing coverage and the Sprint R3 stale-session/revision hardening goal** — specifically stale revision interactions with context frames, intent switches, diary navigation, and confirmation path integration.

---

## Intended Surface / Boundary

| Surface | Tests exist? | Sprint R3 gap |
|---|---|---|
| `InMemoryBernieSessionStore.append_client_event` stale revision rejection | ✅ Full coverage | Stale revision + context frame interaction not tested |
| `InMemoryBernieSessionStore.append_server_outcome_event` stale revision rejection | ✅ Partial | Stale server-outcome revision + ordering edge cases not covered |
| Session routes HTTP stale 409 | ✅ Route-level | Stale revision + context_frames sent together in body not tested |
| `check_staleness()` freshness-id gates | ✅ Module-level | Integration: stale session coord + confirm endpoint path not tested |
| `diary_navigated` vs stale revision | ❌ Not tested | Stale diary_navigated should fail revision guard, not state guard |
| Intent switch (staff_instruction) from stale session | ❌ Not tested | New instruction on stale session should still require correct revision |
| Two concurrent tabs / active session replacement edge cases | ❌ Not tested | New session replaces; interleaved append on old session should fail closed |
| Clarification merge on stale context frames | ❌ Not tested | Context frame merge when session itself is stale should not proceed |
| YAML scenario fixtures for stale-session | ✅ One fixture | Stale reference date; need stale revision + clarification scenarios |

---

## Out of Scope

- Primary production implementation / production code edits to session.py, session_store.py, evidence.py, or routes
- Diary UI / taskpane / Word changes
- Live Gemini / Vertex / LLM provider calls
- Broad unrelated test rewrites or refactoring
- Editing existing R2 tests unless a clear invitation to add a simple edge case exists
- GraphRAG, MCP, or indexer automation
- Global config edits or model switching

---

## Files I Expect To Edit

New test files (preferred — clean boundary, no risk of breaking existing assertions):

1. **`tests/test_deepseek_sprint_r3_stale_session_regression.py`** — Primary regression test file for this lane
2. **`tests/fixtures/bernie_scenarios/stale_session_revision_clarification.yaml`** — Optional YAML scenario fixture

If a small YAML fixture helper or conftest change is needed for scenario loading, that is in scope as a bounded fixture change only.

---

## Implementation Steps

### Step 1: Stale revision + context frame interaction (unit tests on `InMemoryBernieSessionStore`)

Add tests proving that:
- A `staff_instruction` with stale `expected_revision=0` on session at revision=3 rejects with `stale_session_revision` even when valid `context_frames` are in the payload — revision guard fires before any frame processing
- A `clarification_reply` with stale revision on session in `clarification` state rejects with `stale_session_revision` before frame merge
- Idempotent replay still works (already tested, but verify context_frame payload does not break idempotency)

### Step 2: Stale revision + diary navigation

Add tests proving that:
- `diary_navigated` with stale revision on a non-transient session (e.g. `clarification`) rejects with `stale_session_revision`, not the transient-state error
- `diary_navigated` with correct revision on a stale-marked session (session has `stale_reason_code`) succeeds and marks session stale — the stale mark is memory-level, not revision-level

### Step 3: Stale revision + intent switch

Add tests proving that:
- `staff_instruction` with correct revision on a session in `clarification` state succeeds (state transition is valid) even if the session previously rejected a stale attempt
- A stale `staff_instruction` leaves the session unchanged even when the session is in `clarification` (where a valid instruction would transition to `recognition`)

### Step 4: Server outcome stale revision integration

Add tests proving that:
- `interpretation_outcome` with stale `expected_revision` on session at revision=2 rejects with `stale_session_revision`
- Session events list and revision are unchanged after a rejected stale server outcome
- Server outcome ordering is enforced even with stale revision: a `confirmation_outcome` with stale revision on `instruction_entry` rejects for both stale revision AND wrong state

### Step 5: Active session replacement edge cases

Add tests proving that:
- Creating a new session for the same (practice, user, surface) via `create_session` replaces active session
- Appending events to the old session id after replacement still works (old session record is preserved, not deleted — the active pointer changes, not the record)
- A `new_session` event on the old session id replaces active AND resets session state

### Step 6: Confirmation + stale session coordinates (route-level integration)

Add HTTP-level test proving that:
- A confirm-bernie endpoint call with stale session coordinates (wrong session_revision, wrong reference_date, or stale freshness_id) returns a typed block without writing appointments or audit rows
- The staleness codes (`stale_session_revision`, `mismatched_reference_date`, `stale`) surface in the response blocks

### Step 7: YAML scenario fixture (optional, value-dependent)

If the scenario loader supports it, add one fixture:
- `stale_session_revision_clarification.yaml` — two-turn scenario: Turn 1 resolves patient/date; Turn 2 sends stale revision context → session rejects → Turn 3 sends correct revision → merge succeeds

---

## Visual / Behavioural Acceptance Checks

- No existing test in `test_bernie_session_store.py` or `test_bernie_session_routes.py` is deleted or modified (only new tests added)
- Every stale-revision test asserts **both** the rejection AND that the session state/events/revision are unchanged (fail-closed invariant)
- Every intent-switch-success test asserts **both** the acceptance AND that the session advanced to the correct state
- The `diary_navigated` stale test proves the revision guard fires before the state check, not after
- The YAML scenario (if added) passes `pytest tests/bernie_scenarios/test_scenario_replay.py`
- `python -m pytest tests/test_deepseek_sprint_r3_stale_session_regression.py -q` passes or produces only actionable failures (pre-existing infrastructure issues)
- `git diff --check` passes (no whitespace errors)
- `git status --short --branch` is clean except for intended new files

---

## Risks / Ambiguities

1. **`check_staleness()` integration test**: The confirm-bernie endpoint (`POST .../confirm-bernie`) currently expects specific `selection_proposal` format. Writing a full HTTP integration test for stale session + confirm may require mocking session store state through the route. The risk is that the mock setup is complex. Mitigation: test at the `InMemoryBernieSessionStore` and session route levels primarily; add a slim HTTP test only if the setup is tractable.

2. **Python availability in sandbox**: Python is not available in the current DeepSeek sandbox. If `pytest`, `compileall`, or `git diff --check` cannot be run after writing tests, I will leave a clear review artifact (the test files themselves) and document the verification gap for Ariadne.

3. **Scenario fixture path**: If `test_scenario_replay.py` requires specific setup (e.g., scenario registration, loader updates) to discover new YAML fixtures, I may skip the YAML fixture and cover the scenario at the unit level instead.

4. **Boundary between R2 and R3**: Some R2 tests already verify stale revision. R3 must not overlap or conflict. I will add only scenarios that R2 explicitly does not cover — specifically session revision + context frame interaction, intent switch after stale, diary navigation staleness, and confirmation integration.

5. **`append_server_outcome_event` access**: The session routes test uses the HTTP path; the session store test uses direct `InMemoryBernieSessionStore`. My tests should use the direct store for unit-level stale revision tests and the HTTP client for integration-level stale session tests.

6. **PHI guard already proven**: R2 tests already prove PHI payload rejection on the session route. I will not re-test PHI payloads unless the stale revision + PHI combination reveals a new edge case (unlikely).

---

## Dissent / Risks

- **Production code should already handle all these cases correctly.** R2 tests prove the session store guards and route guards work in isolation. The main value of this regression lane is proving that combinations (stale + context, stale + diary_navigation, stale + intent switch) also fail closed and that no regression was introduced in the integrated path.
- **The stale session + confirm integration test** may be better performed by Ariadne using the full route stack than by a regression test that requires mock wiring. If mock setup dominates the test complexity, I will skip it and flag it as a residual risk for the closeout.
- **Session replacement edge cases** are architecture-safe (the session store is in-memory; replacement updates an in-memory pointer, not a DB row), but the tests still prove the contract is observable and stable.
- **No production code changes** — this is purely a regression test lane. If I find a genuine test failure (existing production code does NOT handle a stale+context combination safely), I will capture the finding for Ariadne rather than patching the production code.
