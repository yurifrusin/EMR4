# review-codex-codex-sprint98-bernie-release-gates

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint98-bernie-release-gates` |
| Source Task | `codex-sprint98-bernie-release-gates` |
| Status | queued |

## Review Request

codex-sprint98-bernie-release-gates ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/bernie_release_gates.md`, `review/test_diary_smoke.py`, `scripts/smoke_bernie_interpreter.py`, `tests/test_smoke_bernie_interpreter_script.py`, `tests/test_bernie_sprint98_release_gates.py`, plus this completion note update.
- Verification run: `.venv\Scripts\python.exe -m py_compile scripts\smoke_bernie_interpreter.py tests\test_smoke_bernie_interpreter_script.py tests\test_bernie_sprint98_release_gates.py review\test_diary_smoke.py` passed; `node --check docs\diary\diary.js` passed; `git diff --check` passed; direct smoke script explicit-ID/redaction and ordinary 14:00-15:45 commands passed; `.venv\Scripts\python.exe -m pytest tests\test_smoke_bernie_interpreter_script.py tests\test_bernie_sprint98_release_gates.py -q --tb=short` now blocks on current generic confirm `{"detail":"Practitioner not found"}` 404; `.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py::test_bernie_route_intercepted_selected_slot_can_return_to_candidates -q --tb=short` now blocks on missing selected-slot path back to candidate booking slots. A later subset rerun hit local test DB schema teardown (`relation "practices" does not exist`) after the intentional failing run.
- Remaining risks: These are release gates, not production fixes. They are expected to remain red until the backend confirm contract and Antigravity/UI selected-slot change path satisfy them. Ariadne should merge/reconcile the UI selector names with Antigravity's implementation branch.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-sprint98-bernie-release-gates.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
