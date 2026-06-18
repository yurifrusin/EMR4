# antigravity-gemini-sdk-migration-spike

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | queued |
| Created | 05edbb6 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-gemini-sdk-migration-spike --commit-message "Spike Gemini SDK migration" --message "Gemini SDK migration spike ready for Codex review"` |

## Mission

De-risk the urgent migration away from deprecated `vertexai.generative_models` usage before the 2026-06-24 removal date, preserving existing EMR4 AI behavior.

## Scope

### In Scope

- Inspect current Gemini/Vertex AI imports and calls, especially consultation analysis and scribe paths.
- Use current Google guidance as the north star: the deprecated Vertex AI generative modules are to be replaced by the Google Gen AI SDK (`google-genai`, `from google import genai`, `client.models.generate_content(...)`).
- Add a small compatibility wrapper or minimal migration only if it is safe, narrow, and testable without redesigning prompts.
- Update dependencies/config notes if needed for `google-genai`.
- If a full migration is not safe in this slice, produce a precise spike result in the completion notes: files affected, code changes required, credential assumptions, risks, and recommended next patch.

### Out of Scope

- Do not redesign prompts or clinical coding logic.
- Do not alter diary frontend/backend work.
- Do not implement unrelated AI features.
- Do not remove working behavior unless a replacement is verified.
- Do not push to `master` or `handoff/current` manually.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Finish with the submit command above.

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

- Run a Python import/compile check over touched backend files.
- Run focused tests if existing tests cover the touched AI code.
- If live Gemini calls cannot be run because credentials are unavailable, state that explicitly and verify the code path as far as possible without secrets.
- Confirm whether `vertexai.generative_models` warnings/imports remain.

## Merge Criteria

- Either a safe minimal migration is submitted, or the spike packet gives Codex an exact, low-ambiguity migration plan.
- No diary files are changed.
- Existing consultation/scribe API contracts are preserved.
- Any dependency change is minimal and documented.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Fill this in before submit:

- Files changed:
- Verification run:
- Remaining risks:
