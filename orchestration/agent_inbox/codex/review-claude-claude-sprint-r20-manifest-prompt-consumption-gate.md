# review-claude-claude-sprint-r20-manifest-prompt-consumption-gate

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-r20-manifest-prompt-consumption-gate` |
| Status | queued |

## Review Request

claude-sprint-r20-manifest-prompt-consumption-gate ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `app/services/diary/capability_manifest.py` — added `import json`; `MANIFEST_PROMPT_CONTEXT_MAX_CHARS` (10 000 char budget); `_FORBIDDEN_KEY_PATTERNS` frozenset; `_collect_string_keys`, `_find_write_authority_violations` private helpers; `assert_manifest_prompt_safe(payload)`; `build_manifest_prompt_context()`; `render_manifest_prompt_block(context=None)`; extended `__all__`.
  - `tests/test_bernie_manifest_prompt_consumption.py` — new test module, 19 deterministic tests.

- Verification run:
  - `py_compile app/services/diary/capability_manifest.py tests/test_bernie_manifest_prompt_consumption.py` → OK
  - `pytest tests/test_bernie_manifest_prompt_consumption.py tests/test_bernie_diary_capability_manifest.py -v` → 29 passed (19 new + 10 existing golden tests unchanged)
  - `git diff --check` → OK
  - grep confirms no `generate_content`, `genai.`, `model.generate`, `openai`, or `anthropic` calls in changed files.

- Remaining risks:
  - Keyword-based PHI/credential guard is heuristic (exact key-name matching). Primary safety guarantee remains that the manifest is source-derived from enums/registries only.
  - `render_manifest_prompt_block` is not yet wired into live Bernie prompt assembly — intentionally a non-runtime scaffold per plan.
  - Char budget (10 000) is a fixed constant. If the capability registry grows substantially, the budget assertion in `build_manifest_prompt_context` will raise — prompting a deliberate review rather than silent expansion.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint-r20-manifest-prompt-consumption-gate.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
