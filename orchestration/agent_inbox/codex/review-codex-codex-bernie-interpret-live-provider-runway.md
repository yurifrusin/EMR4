# review-codex-codex-bernie-interpret-live-provider-runway

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-interpret-live-provider-runway` |
| Source Task | `codex-bernie-interpret-live-provider-runway` |
| Status | integrated |

## Review Request

Sprint 64 Bernie live provider runway implementation ready for review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `app/config.py`; `app/schemas/appointments.py`; `app/services/bernie_booking_interpreter.py`; `tests/test_bernie_interpret_booking_instruction.py`; `orchestration/agent_inbox/codex/codex-bernie-interpret-live-provider-runway.md`
- Verification run: `.venv\Scripts\python.exe -m py_compile app\config.py app\schemas\appointments.py app\services\bernie_booking_interpreter.py tests\test_bernie_interpret_booking_instruction.py`; `.venv\Scripts\python.exe -m pytest tests\test_bernie_interpret_booking_instruction.py -q` (11 passed; existing pytest-asyncio loop-scope deprecation warning only); `git diff --check`; targeted `rg` scan for prohibited DB writes, audit writes, proposal/confirm/slot-search helpers, direct SDK calls, and logging in the Bernie interpreter.
- Remaining risks: Live Gemini/Vertex path is still explicit-config only and unexercised against real cloud credentials by design. The provider prompt necessarily sends the staff instruction to the configured live provider when explicitly enabled, but ordinary tests use mocked providers and disabled/fake defaults remain non-live. Exact production model credential setup remains out of scope.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/codex/codex-bernie-interpret-live-provider-runway.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Integrated after Ariadne review and one bounded docstring repair clarifying that only the explicitly configured live provider path may call the AI provider.
- Follow-up required: Future explicit live Gemini/Vertex smoke with Bernie service-account/ADC setup; no Yuri-only test required for this backend default-off sprint.
