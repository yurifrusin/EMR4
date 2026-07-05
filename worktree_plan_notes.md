# DeepSeek Worker Plan Notes — codex-sprint-r5-deepseek-executable-scenario-promotion

## Sandbox status
- Python: NOT AVAILABLE in sandbox
- git: NOT AVAILABLE in sandbox
- Plan packet written manually: orchestration/agent_inbox/codex/codex-executable-scenario-promotion-plan.md
- No production code changes made

## Handin result
- Could not run `python scripts/agent_worktrees.py handin` — python not in sandbox PATH
- Read all 19 NL corpus fixtures, 2 executable fixtures, loader.py, replay.py, test_scenario_replay.py, test_bernie_scenario_integrity.py, test_bernie_slot_normalizer.py, test_bernie_confidence_policy.py, test_bernie_supervised_booking_wrapper.py, receptionist_review_r3.md, receptionist_review_r4.md

## Key findings

### Harness architecture
- NL fixtures: user/expect.outcome/reason_codes structure, skipped by loader via NonExecutableScenario
- Executable fixtures: action/input/expect.fields structure, runs API calls through replay.py
- 4 actions: normalize, search, select, confirm
- No action: interpret or action: supervised-booking exists
- Forbidden-AI-provider guard installed per scenario run

### Promotable candidates (P0 — past-date guardrails)
- absolute_past_date_blocked.yaml ? CLEAN MAPPING: normalize action with past date_from
  - test_bernie_slot_normalizer.py already tests this at unit level (test_absolute_date_from_before_reference_date_blocks)
  - test_bernie_supervised_booking_wrapper.py tests it at supervised-booking endpoint level (test_past_absolute_date_blocks_before_slot_search)
  - But NO executable YAML fixture exists for it yet

- booking_no_matching_times_only_after_slot_search_empty.yaml ? needs investigation of search response shape with empty roster slots

- booking_roster_unavailable_distinct_from_no_slots.yaml ? needs supervised-booking action or stays NL-only

- same_day_past_window_clarify.yaml ? NOT PROMOTABLE: needs simulated_clinic_time injection which replay.py doesn't support

### Not promotable (out of scope for this action set)
- Clarification-merge fixtures: NL interpret flow only
- Stale-session/revision fixtures: need session freshness context
- Extension/pivot fixtures: need appointment-mutation endpoints

## Ariadne request
- Please run: `python scripts/agent_worktrees.py plan --agent codex --task codex-sprint-r5-deepseek-executable-scenario-promotion --summary "Promote R3/R4 past-date guardrail NL fixtures into executable replay coverage" --understanding "..." --surface "..." --out-of-scope "..." --files "..." --steps "..." --acceptance "..." --risks "..."`
  Detailed plan text is in: orchestration/agent_inbox/codex/codex-executable-scenario-promotion-plan.md
- Then submit: `python scripts/agent_worktrees.py submit --agent codex --task codex-sprint-r5-deepseek-executable-scenario-promotion --commit-message "Plan R5 executable scenario promotion" --message "Plan packet submitted; no production code changes."`
