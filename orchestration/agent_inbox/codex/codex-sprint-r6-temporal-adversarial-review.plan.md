# codex-sprint-r6-temporal-adversarial-review — Plan Packet

| Item | Value |
|---|---|
| **Role** | DeepSeek Flash (worker) |
| **Worker name** | Shen |
| **Worker branch** | codex/sprint-r6-temporal-review |
| **Status** | plan_gate (not implemented) |
| **Date** | 2026-07-05 |

## Protocol Note

python is not available in this sandbox. The handin, plan, and submit protocol commands cannot run. This plan artifact is written directly to disk. Ariadne/Codex must run the submit command from the integration worktree if the plan is accepted.

## My Understanding

Adversarially review temporal-boundary coverage in the Bernie booking pipeline. Identify brittle clock dependencies, overfitting risks, and gaps where same-day past-window behaviour cannot be deterministically tested. Recommend whether to add simulated_clinic_time to the replay harness or create a focused pytest route suite.

## Intended Surface / Boundary

**Affected surfaces (read only, no edits):**
- pp/services/diary/temporal.py — pure temporal policy (evaluate_same_day_window)
- pp/routers/appointments.py — route-level call sites for temporal decisions (interpret route ~line 3700, supervised-booking route ~line 5618, waiting-room ~line 2433)
- pp/services/bernie/session_store.py — _utcnow() clock injection gaps
- 	ests/bernie_scenarios/replay.py — replay harness (no clock injection)
- 	ests/bernie_scenarios/loader.py — loader (does not parse simulated_clinic_time)
- 	ests/test_bernie_temporal_policy.py — existing unit tests
- 	ests/test_bernie_confidence_policy.py — existing route-level temporal tests
- 	ests/bernie_scenarios/test_scenario_replay.py — parametrized replay executor
- 	ests/fixtures/bernie_scenarios/same_day_past_window_clarify.yaml — the key non-executable fixture
- 	ests/fixtures/bernie_scenarios/absolute-past-date-blocked-exec.yaml — existing executable past-date fixture
- docs/receptionist_review_r4.md — R4 policy matrix
- docs/receptionist_review_r5_adversarial.md — R5 review findings and outstanding recommendations

**Must not change:**
- No production code edits (app/, alembic/)
- No Diary UI, taskpane, Word assets
- No live provider calls
- No modifications to Claude's R6 implementation lane files
- No changes to the existing replay harness unless explicitly recommended with clear boundary and reason

## Out of Scope

Production code edits, broad harness rewrite, modifying Claude-owned implementation files, Diary UI, taskpane/Word assets, raw appointment mutation date-policy changes, stale-session fixture promotion (requires session-state injection beyond clock).

## Files I Would Edit (if approved to implement)

Recommendation: create docs/receptionist_review_r6_adversarial.md only — no production code or test edits. If Ariadne wants test files, a new 	ests/test_bernie_temporal_boundary_pytest.py or a proposed fixture diff could be created, but the plan gate first requires this classification.

## Implementation Steps (plan-gate-only — no execution)

### Step 1: Classify all temporal clock dependencies (complete below in findings)

### Step 2: Produce docs/receptionist_review_r6_adversarial.md with:
- Clock injection point inventory
- Overfitting risk analysis
- Replay-harness gap: simulated_clinic_time for same-day scenarios
- Recommendation: replay fixture vs. pytest route suite vs. holding pattern
- Concrete proposed test matrix (parameterized pytest module)
- Risk register: remaining untested boundaries

### Step 3: Submit plan via (blocked — needs Ariadne to run submit from integration worktree):
`
python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r6-temporal-adversarial-review --commit-message "Plan R6 temporal adversarial review" --message "Plan packet submitted; no production code changes."
`

## Verification (post-approval)

- Review artifact file docs/receptionist_review_r6_adversarial.md created
- git diff --check must pass
- No production code or harness files modified

## Risks / Ambiguities

1. **Python unavailable**: Cannot run handin, plan, submit, or any pytest verification. This means plan-only submission.
2. **Overlap with Claude's R6 harness work**: The task packet says Claude/Sonnet owns the temporal harness foundation. My adversarial review must not cross into Claude's implementation files. If Ariadne decides a pytest route suite is the right path rather than harness changes, that must be coordinated with Claude's lane.
3. **Session-store clock**: _utcnow() in session_store.py is partially overridable via create_session(now=...), but ppend_event and 	ransition_state lack override parameters. Stale-session detection may be clock-sensitive in ways not covered by temporal-boundary tests.
4. **Waiting-room clock**: get_waiting_room uses datetime.now(practice_tz).date() directly (not _clinic_local_now). This is a separate injection point that existing _clinic_local_now monkeypatches do not cover.

---

## Detailed Findings

### A. Clock Injection Point Inventory

| # | Location | Function | Clock Source | Overridable? | Used By |
|---|---|---|---|---|---|
| 1 | pp/routers/appointments.py:402 | _clinic_local_now() | datetime.now(tz=practice_tz) | ✅ monkeypatch.setattr(router, "_clinic_local_now", ...) | Interpret route (~3709), supervised-booking (~5618) |
| 2 | pp/routers/appointments.py:2433 | get_waiting_room() | datetime.now(practice_tz).date() | ❌ Direct call, not through _clinic_local_now | Waiting room queue |
| 3 | pp/services/bernie/session_store.py:56-57 | _utcnow() | datetime.now(timezone.utc) | Partial — create_session(now=...) accepts override, but ppend_event and 	ransition_state fall back to _utcnow() | Session timestamp generation, stale detection |
| 4 | pp/services/diary/temporal.py | evaluate_same_day_window() | Pure — no clock reads | 🔹 Parameter clinic_now is caller-supplied | All callers |

### B. Existing Temporal Test Coverage

| Test module | What it covers | Clock handling |
|---|---|---|
| 	est_bernie_temporal_policy.py (5 tests) | Pure evaluate_same_day_window decisions: not-same-day, fully-past, clamp-partly, clamp-open-ended, exact-boundary | Uses fixed datetime values — no clock dependency ✅ |
| 	est_bernie_confidence_policy.py (4 temporal tests) | Route-level interpret endpoint: temporal band for same-day fully-past/partly-past/open-ended + past absolute block | Uses monkeypatch.setattr(appointments_router, "_clinic_local_now", ...) with fixed datetime ✅ |
| bsolute-past-date-blocked-exec.yaml | Normalize endpoint: absolute past date blocked before slot search | Fixes date via date_from="2026-07-04", eference_date="2026-07-05" — no clock dependency ✅ |
| same_day_past_window_clarify.yaml | NL corpus: "Book today at 10 AM" simulated at 15:00 | Has simulated_clinic_time: "15:00" but (a) uses user: schema so loader skips it, (b) loader doesn't parse simulated_clinic_time, (c) replay doesn't inject clock ❌ Non-executable |

### C. Overfitting Risks

1. **Route-level tests use fixed times**: 	est_bernie_confidence_policy.py always uses datetime(2026, 7, 15, 14, 0, 0, tzinfo=tz). This is deterministic and correct as a unit test pattern. No overfitting risk.

2. **Replay harness uses real wall clock**: If someone runs the scenario replay at 2 AM, _clinic_local_now() returns a time that might cause same_day_past_window_clarify to accidentally pass even if executed — it tests "10 AM at 15:00" but the real clock says 2 AM, so "10 AM" is NOT past. The fixture would pass when it should fail. This is a **latent overfitting risk**.

3. **No CI-level wall clock dependency**: The existing valid tests (unit + route-level + exec fixture) all pin their time values deterministically. The risk only materializes for new same-day scenarios added to the replay harness without clock injection.

### D. Replay-Harness Gap Analysis

To make same_day_past_window_clarify.yaml executable, the harness needs:

1. **Loader** (loader.py): Parse initial_state.simulated_clinic_time from YAML
2. **Scenario dataclass**: Add simulated_clinic_time: Optional[str] field
3. **Replay context** (eplay.py): When simulated_clinic_time is set, monkeypatch ppointments_router._clinic_local_now with a lambda that returns the fixed time
4. **Fixture**: Convert from user: NL schema to ction: normalize schema

Cost: ~40 lines of code in the harness. Risk: monkeypatch applies to all turns in a scenario, so same-day and non-same-day turns within one scenario would need care.

### E. Recommendation: Replay Fixture vs. Pytest Route Suite

**Option A: Pytest route suite (recommended for R6)**

Create a focused deterministic 	ests/test_bernie_temporal_boundary_pytest.py that:
- Monkeypatches _clinic_local_now with fixed times
- Calls the interpret endpoint and/or normalize endpoint
- Asserts temporal band, blocks, and constraint fields
- Has parameterized matrix for all temporal cases
- No harness changes needed
- Runs with existing forbidden-AI-provider guard

This is the **lowest-risk, lowest-cost** path. Each test case is independently clock-controlled. It follows the "explore once, crystallize into a script, run free forever" pattern from the handover protocol.

**Option B: Replay harness simulated_clinic_time injection**

Needed conceptually for the long-term health of the scenario-corpus approach, but involves harness changes that may overlap with Claude's R6 harness lane. Defer to a dedicated harness sprint unless Claude's lane already plans clock injection.

**Recommendation**: Go with Option A (pytest route suite) for R6 and flag Option B as post-R6 harness improvement. Do not touch the replay harness.

### F. Concrete Proposed Test Matrix (for pytest route suite)

| # | Test Case | date_from | earliest | latest | clinic_now | Expected temporal band / decision |
|---|---|---|---|---|---|---|
| 1 | Future date, no same-day | 2026-07-10 | None | None | 2026-07-05 14:00 | assume (not same-day) |
| 2 | Same-day, window fully past | 2026-07-05 | 09:00 | 10:00 | 2026-07-05 14:00 | ask, window_fully_past |
| 3 | Same-day, earliest past, latest future | 2026-07-05 | 09:00 | 14:00 | 2026-07-05 10:00 | assume, clamp_earliest=10:00 |
| 4 | Same-day, open-ended past start | 2026-07-05 | 09:00 | None | 2026-07-05 10:15 | assume, clamp_earliest=10:15 |
| 5 | Same-day, earliest exactly now | 2026-07-05 | 10:15 | None | 2026-07-05 10:15 | ok (exact boundary) |
| 6 | Same-day, latest exactly now | 2026-07-05 | None | 10:00 | 2026-07-05 10:00 | window_fully_past (latest == now → past) |
| 7 | Same-day, open-ended, no constraint | 2026-07-05 | None | None | 2026-07-05 14:00 | assume, no clamp needed |
| 8 | Absolute past date (pytest, not exec fixture) | 2026-07-04 | None | None | 2026-07-05 14:00 | block, requested_date_in_past |
| 9 | Same-day, earliest after now | 2026-07-05 | 15:00 | None | 2026-07-05 14:00 | assume, no clamp |
| 10 | Same-day, both times after now | 2026-07-05 | 14:30 | 16:00 | 2026-07-05 14:00 | assume, no clamp |

### G. Remaining Untested Boundaries (outside R6 scope)

| Boundary | Why not R6 | Where to address |
|---|---|---|
| Direct raw appointment mutation with past dates | Outside Bernie's slot-search guard entirely; product policy needed first | Post-R6 product-policy sprint |
| Stale session timestamp drift | Requires session-state injection into harness, not just clock | Dedicated session-harness sprint |
| Waiting room datetime.now() at line 2433 | Separate from Bernie's temporal policy; waiting room is a live queue endpoint | Sporadic sprint or when waiting room gets test coverage |
| Session store 	ransition_state clock gap | 	ransition_state at line 302 uses _utcnow() without override; stale-session detection may produce inconsistent timestamps under simulated time | Session-storage hardening sprint |

## Acceptance Checks

- Review artifact classifies all temporal clock dependencies and their test coverage
- Concrete, actionable recommendation is made for R6 (Option A vs. Option B)
- Risk register documents what the review deliberately excludes
- No production code, harness, or test files are modified

