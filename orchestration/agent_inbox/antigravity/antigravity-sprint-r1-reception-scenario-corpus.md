# antigravity-sprint-r1-reception-scenario-corpus

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 788242c |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r1-reception-scenario-corpus --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r1-reception-scenario-corpus --commit-message "Sprint R1 Reception Scenario Corpus" --message "antigravity-sprint-r1-reception-scenario-corpus ready for Codex review"` |

## Mission

Use Gemini as a real receptionist-domain/test-design worker: author the first 8-12 Bernie receptionist scenarios from the R1 workstream, with clear expected structured outcomes, preserved facts, forbidden behaviours, and xfail markers for known unfixed behaviours such as long-appointment clarification merge.

## Scope

### In Scope

1) Read orchestration/bernie_reception_scenario_workstream.md and existing Bernie tests enough to align vocabulary. 2) Create or update scenario fixture files under tests/fixtures/bernie_scenarios/ using the agreed compact schema. 3) Include the seed categories: long appointment clarification preservation, tomorrow not blocked by today's patient booking, no matching times only after slot search, roster unavailable distinct from no slots, extend-by versus make-total semantics, confirmation required before mutation, and stale latest-message guard. 4) Add scenario-level notes/dissent where receptionist wording or expected state is ambiguous. 5) Keep scenarios human-readable and easy for future Yuri findings to extend.

### Out of Scope

No backend replay harness implementation. No production app code. No Diary UI changes. No GraphRAG, prompt rewrite, production log ingestion, PHI, auto-mode, or mutation behaviour changes. Do not remove or rewrite existing tests.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

If the harness/schema validator exists by implementation time, run the focused scenario fixture validation. Otherwise run any available YAML/JSON parse check and record manual schema checklist coverage; git diff --check

## Merge Criteria

Corpus contains 8-12 high-value receptionist scenarios, each has explicit expectations and forbidden behaviours, known bugs are marked xfail rather than hidden, no production code is touched, and Gemini domain dissent is captured for Ariadne

## Dissent / Risks

No receptionist-domain dissent. The 9 selected scenarios cover the core practice grammar bugs identified. Known bugs (like clarification merges re-asking for practitioner) are flagged as `xfail` with a detailed reason referencing Sprint R2.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - tests/fixtures/bernie_scenarios/README.md (new)
  - tests/fixtures/bernie_scenarios/booking_clarify_long_duration_preserves_practitioner.yaml (new)
  - tests/fixtures/bernie_scenarios/booking_clarify_long_duration_preserves_patient_date_time.yaml (new)
  - tests/fixtures/bernie_scenarios/booking_tomorrow_not_blocked_by_patient_booking_today.yaml (new)
  - tests/fixtures/bernie_scenarios/booking_no_matching_times_only_after_slot_search_empty.yaml (new)
  - tests/fixtures/bernie_scenarios/booking_roster_unavailable_distinct_from_no_slots.yaml (new)
  - tests/fixtures/bernie_scenarios/extend_by_15_minutes_distinct_from_make_30_total.yaml (new)
  - tests/fixtures/bernie_scenarios/clarification_reply_merges_missing_field_only.yaml (new)
  - tests/fixtures/bernie_scenarios/confirm_required_before_create_or_update.yaml (new)
  - tests/fixtures/bernie_scenarios/refresh_does_not_resurrect_stale_latest_message.yaml (new)
- Verification run:
  - YAML syntax check: Successfully parsed all 9 scenarios using PyYAML library (`C:\Users\sarashera\emr4\.venv\Scripts\python.exe -c "import yaml, glob; [yaml.safe_load(open(f, encoding='utf-8')) for f in glob.glob('tests/fixtures/bernie_scenarios/*.yaml')]"`).
- Remaining risks:
  - Schema alignment mismatch if Claude's parser or Codex's validator deviates from the YAML properties. This is mitigated by documenting the schema clearly in the README.md.
