# Sprint R5 Adversarial Scenario Review: Corpus Executability & Past-Date Promotion Analysis

| Item | Value |
|---|---|
| **Reviewer** | DeepSeek Flash (worker: codex/sprint-r5-scenario-review) |
| **Source task** | `codex-sprint-r5-deepseek-scenario-adversarial-review` |
| **Branch** | `codex/sprint-r5-scenario-review` |
| **Date** | 2026-07-05 |
| **Review surface** | All 18 YAML scenario fixtures in `tests/fixtures/bernie_scenarios/` + the replay harness `tests/bernie_scenarios/` |
| **Approved** | Complete sprint task |

---

## 1. Executive Summary

The R3 and R4 Bernie receptionist scenarios introduced valuable domain semantics — stale-session guards, concurrency prevention, correction/pivot semantics, and absolute-past-date blocking — but **none of these scenarios are executable by the replay harness**. All 14 corpus-memory scenarios from R1–R4 remain natural-language descriptions only. The replay harness covers only 2 harness-demo mechanical fixtures.

**The implementation lane's likely past-date promotion (R4) was correctly scoped to backend route tests and unit coverage** (`test_bernie_slot_normalizer.py`, `test_bernie_confidence_policy.py`, `test_bernie_supervised_booking_wrapper.py`). The NL corpus fixtures captured the policy intent. However, the gap between NL corpus memory and executable replay invites regressions: if a future refactor breaks the normalizer or confidence policy, the corpus fixtures will silently report nothing because they are never run.

**Recommendation**: Do **not** promote the R4 corpus fixtures as-is into executable harness scenarios. Instead, create a focused subset of parameterized harness scenarios that exercise the temporal-policy endpoints (normalize → search → confirm) for past-date cases, and add harness support for session-stale state injection before promoting any R3 concurrency fixtures.

---

## 2. Full Corpus Classification

### 2A. Harness-Executable Scenarios (action: normalize|search|select|confirm)

These use the canonical replay-harness schema and run as parametrized pytest cases.

| # | Fixture | Sprint | Verdict | Notes |
|---|---|---|---|---|
| 1 | `harness_demo_happy_path.yaml` | R1 | ✅ Passes | Mechanical proof of harness; owned by Claude |
| 2 | `harness_demo_clarification_merge_xfail.yaml` | R1 | ✅ xfail (known) | Demonstrates xfail mechanism for R2 target |

**Count: 2 out of 18 (11%)**

### 2B. Natural-Language Corpus Memory (user: turns — NOT executable)

These describe NL receptionist turns and expected outcomes. The harness rejects them at load time because the `loader.py` requires `action:` in each turn and raises `NonExecutableScenario` for any fixture with `user:` instead.

#### R1/R2 Clarification Merge Semantics (xfail marked)

| # | Fixture | Sprint | Has `forbidden:`? | Has `forbidden_outcomes:`? | Verdict |
|---|---|---|---|---|---|
| 3 | `booking_clarify_long_duration_preserves_patient_date_time.yaml` | R1 | ✅ | ❌ | Corpus memory; xfail (clarification merge bug) |
| 4 | `booking_clarify_long_duration_preserves_practitioner.yaml` | R1 | ✅ | ❌ | Corpus memory; xfail (clarification merge bug) |
| 5 | `clarification_reply_merges_missing_field_only.yaml` | R1 | ✅ | ❌ | Corpus memory; xfail (clarification merge bug) |

**Risk**: The xfail markers are stale. These were scheduled for Sprint R2 fix. The closeout shows R2 intent-switch work happened, but these 3 xfail fixtures remain un-xfailed, indicating the clarification merge bugs may still be unresolved or the fixtures were never validated against the current backend.

#### R2 Intent Switch & Extension

| # | Fixture | Sprint | Has `forbidden:`? | Verdict |
|---|---|---|---|---|
| 6 | `booking_to_extension_switch_during_clarification.yaml` | R2 | ✅ | Corpus memory; no xfail — describes pivot semantics that may pass through interpreter |
| 7 | `extend_by_15_minutes_distinct_from_make_30_total.yaml` | R2 | ✅ | Corpus memory; describes extension vs update semantics |

#### R3 Stale-Session / Revision Hardening

| # | Fixture | Sprint | Has `forbidden:`? | xfail? | Verdict |
|---|---|---|---|---|---|
| 8 | `stale_session_concurrency_conflict.yaml` | R3 | ✅ | ❌ | Corpus memory; needs `expected_revision` injection in harness |
| 9 | `stale_session_reload_blocking.yaml` | R3 | ✅ | ❌ | Corpus memory; needs `stale: true` session setup in harness |
| 10 | `stale_session_correction_and_pivot.yaml` | R3 | ✅ | ❌ | Corpus memory; needs seeded appointments + state injection |
| 11 | `refresh_does_not_resurrect_stale_latest_message.yaml` | R3 | ✅ | ❌ | Corpus memory; needs session-freshness harness support |
| 12 | `stale_reference_date_confirmation_blocked.yaml` | R3 | ❌ | ✅ | Corpus memory; explicitly marked corpus memory in xfail reason |

#### R4 Past-Date Safety

| # | Fixture | Sprint | Has `forbidden:`? | xfail? | Verdict |
|---|---|---|---|---|---|
| 13 | `absolute_past_date_blocked.yaml` | R4 | ✅ | ❌ | Corpus memory; captures policy intent for blocking before slot search |
| 14 | `same_day_past_window_clarify.yaml` | R4 | ❌ | ❌ | Corpus memory; no `forbidden:` — weakest fixture in corpus |

#### Other Domain Scenarios

| # | Fixture | Sprint | Verdict |
|---|---|---|---|
| 15 | `booking_tomorrow_not_blocked_by_patient_booking_today.yaml` | R1 | Corpus memory (advisory) |
| 16 | `booking_no_matching_times_only_after_slot_search_empty.yaml` | R1 | Corpus memory (no-slot outcome) |
| 17 | `booking_roster_unavailable_distinct_from_no_slots.yaml` | R1 | Corpus memory (roster outcome) |
| 18 | `confirm_required_before_create_or_update.yaml` | R1 | Corpus memory (mutation safety) |

**Count: 16 out of 18 (89%)**

---

## 3. Harness Limitations Preventing Executability

### 3A. Schema Mismatch (Blocking All 16 NL Fixtures)

The `loader.py` (`tests/bernie_scenarios/loader.py`) enforces:

```python
KNOWN_ACTIONS = frozenset({"normalize", "search", "select", "confirm"})
```

Any fixture with `user:` turns raises `NonExecutableScenario` and is silently skipped at discovery time. The corpus memory fixtures use an entirely different schema (`user:` / `expect: outcome:` / `reason_codes:` / `preserved:`) that the harness parser cannot interpret.

**Impact**: 100% of domain-authored scenarios are non-executable. No CI failure can catch regressions in the described behaviour.

### 3B. No NL Interpreter Stub

The replay harness installs an AI-provider guard that raises `AssertionError` if any provider call is attempted. This is correct — we must not call Gemini during testing — but the NL corpus scenarios inherently require an interpreter to go from `user: "Book an appointment for yesterday at 10 AM"` to the `normalize` request that the harness understands. An interpreter call is the only path from natural language to structured API actions.

Without a server-side interpreter stub that produces deterministic outputs from known inputs, NL scenarios cannot be replayed. Building such a stub is a substantial harness capability, not a quick schema change.

### 3C. No Simulated Clinic Time

The `same_day_past_window_clarify.yaml` fixture depends on `simulated_clinic_time: "15:00"` in initial_state. The replay harness (`replay.py`) has no mechanism to inject a simulated current time into the server — it uses the system clock and the fixed `reference_date` parameter only.

### 3D. No Session State Injection

R3 fixtures require `stale: true`, `session_id: "session_old_1"`, and `expected_revision` semantics. The harness currently:
- Creates a fresh session per scenario run (via conftest fixtures)
- Has no concept of a "stale" session or revision counter
- Cannot inject pre-existing session state

Enablement work needed: a session-state factory that can produce stale sessions with known revision numbers, plus a route-level revision guard that the harness can assert against.

### 3E. No `forbidden:` Enum Mapping

The 16 NL fixtures use a free-text `forbidden:` list (e.g. `"run slot search"`, `"show candidates"`, `"raise same_day_collision warning"`). The executable harness uses a controlled enum `forbidden_outcomes: ["provider_called", "appointment_written", "audit_written"]`. There's no mapping between the free-text descriptions and the enum. Any future `forbidden:` → `forbidden_outcomes:` conversion would need to decide whether to:
- Broaden the enum to include semantic outcomes like `slot_search_run` and `candidates_shown`
- Keep the enum narrow and validate the free-text list only in a static lint rule

---

## 4. Past-Date Promotion Analysis

### R4 Implementation Surface (Already Verified)

The R4 closeout confirms:

- `requested_date_in_past` added to the shared Bernie slot-search normalizer
- Interpret route temporal axis aligned to report `block` for past dates
- Route regressions proving interpret and supervised-booking paths block before executable slot search
- Unit coverage for past, same-day, future, relative today/tomorrow, and no-reference normalizer boundaries

These were tested via `test_bernie_slot_normalizer.py`, `test_bernie_confidence_policy.py`, and `test_bernie_supervised_booking_wrapper.py` — **not** via scenario replay.

### Should the NL Past-Date Fixtures Be Promoted to Executable Harness?

**Verdict: NO, not as-is.** But partial promotion is feasible and recommended.

| Reason | Detail |
|---|---|
| **NL → action translation gap** | The past-date fixtures (13, 14) are NL. Making them executable requires either an interpreter stub or converting them to deterministic `normalize` calls with known `date_from` < `reference_date` — which the unit tests already cover. |
| **Route-blocking already verified** | The route-level regression tests prove the interpret and supervised-booking paths block before slot search. A harness replay would cover the same code path redundantly. |
| **Same-day past window requires time injection** | Fixture 14 needs `simulated_clinic_time`. Without harness support for time simulation, this fixture cannot be promoted. |
| **Value of executable harness coverage** | If the normalizer or confidence-policy code moves to a new module or gets refactored, the unit tests will catch regressions. Harness coverage adds end-to-end route-level safety, which is valuable but lower priority than unit coverage. |

### Recommendation

1. **Do convert** `absolute_past_date_blocked.yaml` into a harness fixture: replace the `user:` turn with a deterministic `normalize` action that sends `date_from: "2026-07-04"` (yesterday) against `reference_date: "2026-07-05"`, and assert `safe: false` and `constraint.date_from` blocked. This is a simple translation requiring no harness changes.
2. **Keep** `same_day_past_window_clarify.yaml` as corpus memory until the harness supports `simulated_clinic_time` injection.
3. **Keep all R3 stale-session fixtures** as corpus memory. They require non-trivial harness enablement (session-state injection, revision counters).

---

## 5. Concrete Future-Harness Follow-Up

### Create a Parameterized Temporal-Policy Harness Suite

The single most valuable harness improvement is a dedicated pytest module (`tests/bernie_scenarios/test_temporal_boundary.py`) that takes the deterministic path:

```python
# Proposed skeleton (not production code — just the review recommendation)
PARAMETERS = [
    ("past_date_absolute",  "2026-07-04",  {"date_from": "2026-07-04"},   {"safe": False, "code": "requested_date_in_past"}),
    ("past_date_yesterday", "2026-07-05",  {"date_from": "yesterday"},    {"safe": False, "constraint.date_from": "2026-07-04", "code": "requested_date_in_past"}),
    ("future_date_ok",      "2026-07-05",  {"date_from": "2026-07-14"},   {"safe": True}),
    ("today_ok",            "2026-07-05",  {"date_from": "today"},        {"safe": True, "constraint.date_from": "2026-07-05"}),
]
```

This would be:
- **Deterministic**: no NL interpretation, no AI provider calls
- **Narrow**: exercises only the `normalize` endpoint with temporal bounds
- **Easily extensible**: add new parameter sets as new date policies are defined
- **CI-safe**: runs with the existing forbidden-AI-provider guard

This follows the pattern "explore once, crystallize into a script, run free forever" from the handover protocol.

**Follow-up work items**:

1. Add `simulated_clinic_time` injection to the replay harness (`ReplayContext` or fixture scope) so same-day past-window scenarios can be promoted
2. Convert `absolute_past_date_blocked.yaml` to a deterministic `normalize`-only harness fixture
3. After harness session-state injection exists, convert at least `stale_session_reload_blocking.yaml` (simplest R3 fixture — single turn, obvious stale-block outcome)
4. Decide whether to update or retire the 3 xfail R1 clarification fixtures: if the merge bug is resolved, remove `xfail` and convert to executable form; if unresolved, update the xfail reason or promote to a sprint backlog

---

## 6. Open Dissent / Structural Observations

### Corpus Integrity Drift Risk

The corpus memory schema (`user:` / `expect: outcome:` / `reason_codes:`) diverges from the harness schema (`action:` / `input:` / `expect: fields:` / `forbidden_outcomes:`). These are two parallel annotation systems with no automated consistency check. A scenario could be updated in corpus memory to describe behaviour that the backend no longer implements, and no test would fail.

**Recommendation**: Add a post-load integrity check in `loader.py` that warns when a fixture with `user:` fields exists alongside executable fixtures but only the executable ones are parametrized. The check would not block CI but would surface drift in the test output.

### No Regression Tests for the Two Executable Fixtures

The harness-demo fixtures (`harness_demo_happy_path.yaml`, `harness_demo_clarification_merge_xfail.yaml`) are owned by "Claude/harness" and have not been updated since R1. If the backend's normalize/search/select/confirm endpoints change their response schemas, these fixtures will catch the break. But they are mechanical demos, not domain scenarios.

### The `forbidden:` Field Is Unvalidated in Corpus Fixtures

The corpus memory fixtures use `forbidden:` (a free-text list). The harness schema uses `forbidden_outcomes:` (controlled enum). The free-text `forbidden:` field is never parsed or validated — it's human-readable intent only. This means:

- `absolute_past_date_blocked.yaml` says `forbidden: ["run slot search", "show candidates"]` → no machine-verifiable check exists
- `stale_session_concurrency_conflict.yaml` says `forbidden: ["mutate diary state with stale session revision", "confirm booking proposal when expected revision mismatches"]` → purely aspirational

A concrete improvement: add a `load-time only` warning in `loader.py` when a fixture has free-text `forbidden:` but no corresponding `forbidden_outcomes:`, flagging that the fixture's negative assertions are unenforced.

---

## 7. Summary Recommendations

| Decision | Fixtures | Rationale |
|---|---|---|
| **Convert to executable now** | `absolute_past_date_blocked.yaml` | Simple deterministic normalize turn; no harness changes needed |
| **Keep as corpus memory** | `same_day_past_window_clarify.yaml` | Needs simulated clinic time harness support |
| **Keep as corpus memory** | All 5 R3 stale-session fixtures | Need session-state injection — non-trivial harness enablement |
| **Review and reconcile** | 3 xfail R1 clarification fixtures | Stale xfail markers; determine if merge bug is resolved |
| **Create new harness module** | New `test_temporal_boundary.py` | Parameterized normalize-only coverage for all date boundary cases |
| **Add integrity warning** | All corpus memory fixtures | Warn in loader when `user:` fixtures have unenforced `forbidden:` |

---

*This review artifact is the submission for `codex-sprint-r5-deepseek-scenario-adversarial-review`. No production code or test harness files were changed.*
