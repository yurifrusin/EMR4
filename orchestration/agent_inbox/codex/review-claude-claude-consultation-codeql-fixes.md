# review-claude-claude-consultation-codeql-fixes

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-consultation-codeql-fixes` |
| Status | queued |

## Review Request

claude-consultation-codeql-fixes ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-consultation-codeql-fixes.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
