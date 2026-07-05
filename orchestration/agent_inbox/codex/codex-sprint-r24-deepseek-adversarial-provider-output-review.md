# codex-sprint-r24-deepseek-adversarial-provider-output-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/current` |
| Status | ready_for_codex_review |
| Created | 4185731 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-sprint-r24-deepseek-adversarial-provider-output-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-sprint-r24-deepseek-adversarial-provider-output-review --commit-message "Sprint R24 DeepSeek adversarial provider-output review" --message "codex-sprint-r24-deepseek-adversarial-provider-output-review ready for Codex review"` |

## Mission

Second DeepSeek Flash lane: independently review R24 provider dry-run fixture risks and propose adversarial model-style outputs for frame-shape, write-authority, PHI, availability, and ambiguity-default bypasses.

## Scope

### In Scope

adversarial review artifact or non-overlapping tests around manifest_eval provider-style samples

### Out of Scope

Live AI calls, production prompt wiring, frontend UI, DB/migrations, mutation routes

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

Return focused pytest or precise review artifact; run py_compile/pytest if files are changed

## Merge Criteria

Ariadne receives independent adversarial provider-output coverage without overlapping implementation unnecessarily

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - NEW: `orchestration/provider_output_adversarial_review.md` ? structured adversarial review artifact with 42 model-style sample outputs across 8 threat categories (frame-shape, write-authority vocabulary, PHI casing, availability synonyms, ambiguity-default synonyms, confirmation-bypass phrasings, nested write claims, multi-frame/list handling). Each sample includes expected violation kinds, rationale, and documented gap status.
  - NEW: `tests/test_adversarial_provider_outputs.py` ? 44 deterministic, no-DB pytest tests covering: 9 frame-shape detection checks, 6 write-authority coverage/detection-gap tests, 8 PHI casing/underscore gap tests, 6 availability synonym gap tests, 5 ambiguity-default gap tests, 5 confirmation-bypass phrasing gap tests, 3 nested write claim coverage tests, 3 multi-frame/list output handling tests.
- Verification run:
  - `python -m py_compile tests/test_adversarial_provider_outputs.py` ? clean.
  - `pytest tests/test_adversarial_provider_outputs.py -v` ? `44 passed` (0 failed, no DB needed).
  - Pre-existing tests unaffected (same DB-dependent errors as baseline).
- Remaining risks:
  - WA-5 (capital W write claim): the `_check_writes_authorized` case-sensitivity gap is the highest-severity finding ? a capital `W` in `Writes_Authorized` bypasses both the key-set check (lowered `writes_authorized` deliberately excluded from banned set) and the structural check (`.get("writes_authorized")` is case-sensitive). Verified experimentally: `safe=True` even with `Writes_Authorized: True` when `writes_authorized: False` satisfies the schema.
  - PHI casing gap (PH-1 through PH-4): PascalCase/camelCase PHI keys like `DateOfBirth`, `MedicareNumber`, `PatientID` are invisible after lowering because `_PHI_KEY_PATTERNS` uses underscore-separated names. Set intersection is exact-match, so `medicarenumber` ? `medicare`.
  - Multi-frame/list (ML-1): `evaluate_manifest_response` crashes with AttributeError/TypeError on `list[dict]` input. A provider that returns multiple frames per turn cannot be evaluated by the current single-dict entry point.
  - All gaps documented with test evidence; none are production code changes.
