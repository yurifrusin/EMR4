# codex-bernie-interpret-live-provider-runway

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/bernie-interpret-live-provider-runway` |
| Status | submitted |
| Created | 6ed087e |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-interpret-live-provider-runway --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-interpret-live-provider-runway --commit-message "Dispatch Sprint 64 Bernie live provider runway" --message "Sprint 64 dispatched for Codex worker plan gate"` |

## Mission

Add the next safe backend runway for Bernie booking-instruction interpretation: a real Gemini/Vertex provider path behind explicit configuration, while preserving the existing disabled/default-safe and deterministic fake-provider behaviour.

## Scope

### In Scope

app/services/bernie_booking_interpreter.py; app/config.py; appointment schemas/router only if the existing provider envelope requires a narrow compatible field; focused tests for disabled/fake/mocked-live provider behaviour, prompt safety, no writes, no audit rows, no proposal/confirm/slot-search mutation; minimal docs or env-example notes if needed for new config names.

### Out of Scope

Frontend/UI changes; live staff-visible enablement; service-account creation; committing secrets or key files; real appointment/proposal/confirm writes; slot-search execution changes; broad AI-provider refactor outside the existing Bernie interpreter seam; enabling Gemini/Vertex by default; PHI-heavy logging; live cloud calls in ordinary tests.

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

py_compile touched backend files; focused pytest for Bernie interpret provider behaviour; source/test proof that default config remains disabled, tests use fake or mocked provider only, no appointment/proposal/audit/confirm writes occur, and no live LLM call happens unless explicitly configured outside tests; git diff hygiene.

## Merge Criteria

Plan packet accepted first; implementation is narrow and default-off; deterministic tests pass; no secrets or PHI logging; no autonomous booking or database mutation; existing Sprint 63 endpoint contract remains backward compatible.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `app/config.py`; `app/schemas/appointments.py`; `app/services/bernie_booking_interpreter.py`; `tests/test_bernie_interpret_booking_instruction.py`; `orchestration/agent_inbox/codex/codex-bernie-interpret-live-provider-runway.md`
- Verification run: `.venv\Scripts\python.exe -m py_compile app\config.py app\schemas\appointments.py app\services\bernie_booking_interpreter.py tests\test_bernie_interpret_booking_instruction.py`; `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpret_booking_instruction.py -q` (11 passed; existing pytest-asyncio loop-scope deprecation warning only); `git diff --check`; targeted `rg` scan for prohibited DB writes, audit writes, proposal/confirm/slot-search helpers, direct SDK calls, and logging in the Bernie interpreter.
- Remaining risks: Live Gemini/Vertex path is still explicit-config only and unexercised against real cloud credentials by design. The provider prompt necessarily sends the staff instruction to the configured live provider when explicitly enabled, but ordinary tests use mocked providers and disabled/fake defaults remain non-live. Exact production model credential setup remains out of scope.
