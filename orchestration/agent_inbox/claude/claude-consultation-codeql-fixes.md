# claude-consultation-codeql-fixes

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | fca99d2 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-consultation-codeql-fixes --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-consultation-codeql-fixes --commit-message "Consultation CodeQL fixes" --message "claude-consultation-codeql-fixes ready for Codex review"` |

## Mission

Plan and then implement a focused backend fix for the open high/medium CodeQL alerts in app/routers/consultation.py: path-injection around audio_url cleanup, clear-text logging of sensitive consultation/transcription content, stack-trace exposure, and the silent exception noted by baseline review.

## Scope

### In Scope

app/routers/consultation.py; focused backend tests if an adjacent test location exists; minimal helper functions needed to safely validate local temp-file cleanup paths and return bounded error/log messages.

### Out of Scope

No diary/taskpane/UI changes, no migrations, no auth/RBAC redesign, no Gemini prompt or model behaviour changes beyond preserving existing behaviour with safer logging/error handling, no broad route refactor.

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

Before submit, run python -m py_compile app/routers/consultation.py and the most relevant focused pytest tests you can identify; run Bandit focused on app/routers/consultation.py if available. Include exact commands/results in Completion Notes.

## Merge Criteria

All targeted consultation CodeQL issues are addressed without changing successful API behaviour; errors are bounded and user-safe; logs avoid raw consultation/transcription content; verification passes or any blocker is documented.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

- Files changed:
  - `app/routers/consultation.py` — 5 fixes:
    1. **HIGH path injection fixed**: added module-level `_AUDIO_DIR = os.path.abspath(os.path.join("static","audio"))` and `_safe_audio_cleanup(audio_url)` helper that resolves the path with `os.path.abspath`, checks it starts with `_AUDIO_DIR + os.sep`, and only calls `os.remove` if within bounds. `finalize_consultation` now calls `_safe_audio_cleanup(payload.audio_url)` instead of the old `lstrip`+`os.remove` inline.
    2. **MEDIUM PHI logging fixed**: `analyze_consultation` and `scribe_consultation` no longer log diagnosis names or drug names. Replaced `Dx=[names] | Rx=[names]` with `dx_count=N | rx_count=N` in both log lines (MBS item numbers and consultation type are billing metadata, retained).
    3. **MEDIUM stack-trace exposure fixed**: `scribe_consultation` except clause now prints `[scribe] Gemini error: {e}` to stdout and returns generic `{"error": "Transcription failed. Please try again."}` instead of `str(e)`.
    4. **LOW silent except/pass fixed**: `_search_mbs_rules` inner `except Exception: pass` replaced with `except Exception as json_err: print(f"[mbs-rules] skipped malformed JSON result: {type(json_err).__name__}")`. B110 trigger eliminated (except body no longer bare pass).
    5. **MEDIUM raw DB exception in response fixed**: `analyze_consultation` save block and `finalize_consultation` except clause both now print the full exception to stdout and return the generic message `"Encounter save failed. Please contact support."` to the client.
  - `tests/test_finalize_scoping.py` — 2 new tests added:
    - `test_finalize_audio_url_traversal_is_ignored`: constructs a traversal URL that would resolve to a `tmp_path` sentinel file outside `static/audio/`; verifies finalize succeeds (`_saved=True`) and the sentinel file is NOT deleted.
    - `test_finalize_audio_url_valid_path_cleaned`: creates a real file in `static/audio/`; verifies finalize succeeds and the file IS deleted (cleanup worked for a valid in-bounds path).

- Verification run:
  - `python -m py_compile app/routers/consultation.py` → **PASS**
  - `python -m bandit -r app/routers/consultation.py -ll -ii -c pyproject.toml` → **No issues identified** (353 lines scanned, 0 medium+/high findings)
  - `python -m pytest tests/test_finalize_scoping.py -v` → **5 passed** in 56.27s (3 existing + 2 new)
    - `test_finalize_own_patient_succeeds` PASSED
    - `test_finalize_cross_practice_patient_rejected` PASSED (existing "not found" assertion still passes — that path is the explicit JSONResponse at line 378, unchanged)
    - `test_finalize_without_patient_id_uses_default` PASSED
    - `test_finalize_audio_url_traversal_is_ignored` PASSED
    - `test_finalize_audio_url_valid_path_cleaned` PASSED

- Remaining risks:
  - `_AUDIO_DIR` is computed at module import using the process CWD. This is the same assumption as the existing `static/audio` path in `scribe_consultation` (lines 310-312). If uvicorn is ever started from a non-project-root directory, both the audio file creation and the cleanup boundary would shift together — not worse than current behaviour.
  - The generic `_save_error` in exception paths loses per-error diagnosability for production debugging. Mitigated: the full `str(e)` is printed to server stdout before returning the generic message, so logs remain actionable.
  - `B110` (`try_except_pass`) in `_search_mbs_rules` is now resolved by the log statement. The outer `except Exception as e: print(...)` at line 126 (Vertex AI Search error fallback) is LOW severity and filtered by `-ll`; it was pre-existing and does not expose client-facing data.
  - No behaviour change to successful API paths. The `finalize` endpoint's explicit "Patient X not found" JSONResponse (line 378) is unchanged, preserving the existing cross-practice rejection test.
