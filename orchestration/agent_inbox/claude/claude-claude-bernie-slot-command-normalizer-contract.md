# claude-claude-bernie-slot-command-normalizer-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 3da4e2b |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-claude-bernie-slot-command-normalizer-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-claude-bernie-slot-command-normalizer-contract --commit-message "Claude Bernie Slot Command Normalizer Contract" --message "claude-claude-bernie-slot-command-normalizer-contract ready for Codex review"` |

## Mission

Plan first, then after approval add a deterministic backend contract for normalizing Bernie/reception slot-search command input into the existing SlotSearchProposalIn constraint shape without running a search or creating appointments.

## Scope

### In Scope

Plan packet first. After approval, backend command-normalization schemas/service/tests only as needed, likely app/schemas/appointments.py or a small appointments/Bernie helper plus focused tests. Accept structured or LLM-like JSON/dict input, validate/normalize dates, times, practitioner/patient/location/type identifiers where possible, and output a SlotSearchProposalIn-compatible constraint object plus warnings/blocks/summary. Must not call LLMs, must not call the slot-search endpoint, and must not mutate appointments or audit rows.

### Out of Scope

Diary UI, live Bernie runtime, Gemini/LLM calls, autonomous tool execution, appointment creation/search execution, taskpane, Command Centre, SMS, billing, patient demographics, resource admin, database migrations unless strictly unavoidable, and broad scheduling redesign.

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

Plan packet first. After approval: py_compile touched backend modules/tests, focused pytest covering accepted input shapes, invalid/missing constraints, date/time normalization, non-mutation proof, no LLM/search execution, and git diff --check.

## Merge Criteria

Codex can verify a deterministic, non-mutating command-normalization contract that safely produces the typed slot-search constraint shape for future Bernie workflows, with focused tests passing and no runtime UI/LLM/search execution changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - EDIT app/schemas/appointments.py — added `Any`, `ConfigDict` imports; new `SlotSearchCommandIn` (permissive input, extra=ignore, all fields Optional[Any]) and `SlotSearchCommandResult` (safe bool, constraint Optional[SlotSearchProposalIn], warnings/blocks list[AppointmentProposalIssue], summary str) appended after existing slot-search schemas.
  - NEW app/services/bernie_slot_normalizer.py — pure `normalize_slot_search_command(payload, *, reference_date=None)` function. No DB, no network, no LLM. Helpers: `_parse_uuid`, `_parse_date` (handles relative tokens "today"/"tomorrow" only when reference_date injected), `_parse_time`, `_coerce_int`. Enforces: UUID/format parsing only (no DB name→UUID resolution); ISO dates + optional relative tokens; HH:MM/HH:MM:SS times; positive int coercion for duration_minutes; limit clamped to 100 with warning; date_to defaults to date_from when absent; missing practitioner_id/date_from → typed block; delegates ≤14-day range and date_to≥date_from to SlotSearchProposalIn validator; ValueError there → constraint_validation_error block.
  - NEW tests/test_bernie_slot_normalizer.py — 30 pure unit tests. No DB, no server, no network. Covers: well-formed dict, native UUID/date/time types, string coercion, optional fields, date_to default, HH:MM:SS time, limit within range, limit as string, limit clamped with warning, extra LLM keys ignored, relative "today"/"tomorrow" with reference_date, relative token without reference_date blocks, missing practitioner_id/date_from (separately and together), malformed UUID/date/time, non-positive duration, non-positive limit, date_to<date_from constraint error, >14-day range constraint error, purity (no DB/LLM imports in module src), idempotence, no db/session parameter, constraint=None on block, summary populated on success and failure.

- Verification run:
  - py_compile app/schemas/appointments.py app/services/bernie_slot_normalizer.py tests/test_bernie_slot_normalizer.py → OK
  - pytest tests/test_bernie_slot_normalizer.py -v → 30 passed in 30.98s (Python 3.11.7)
  - grep app/services/bernie_slot_normalizer.py for sqlalchemy/google.genai/httpx/requests/asyncpg → none found
  - git diff --check → clean

- Remaining risks:
  - No live slot-search or appointment endpoint is exposed; this is a pure service slice as scoped. Route wiring is a clean next step for Codex to dispatch.
  - Identifier normalization is UUID/format parsing only; DB name→UUID resolution was explicitly out of scope (noted in plan). Downstream /proposals/slot-search already does existence checks.
  - "today"/"tomorrow" relative tokens are the only deterministic relative dates supported. NL-style dates ("next Monday") remain the LLM's responsibility upstream.
