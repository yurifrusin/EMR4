# review-claude-claude-ai-provider-boundary-facade

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-ai-provider-boundary-facade` |
| Status | queued |

## Review Request

claude-ai-provider-boundary-facade ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - NEW app/services/ai/__init__.py — exports AiService
  - NEW app/services/ai/contracts.py — AiCapability enum, AiResult wrapper, ClinicalExtractionData / AudioScribeData / LetterDraftingData permissive Pydantic models, AiProvider Protocol
  - NEW app/services/ai/providers/__init__.py — empty package init
  - NEW app/services/ai/providers/gemini.py — single home for google.genai imports; GeminiProvider.generate_json; handles audio dict -> types.Part.from_bytes so callers never import google.genai
  - NEW app/services/ai/service.py — AiService facade with analyze_consultation_text / scribe_audio / draft_letter; uses asyncio.to_thread; lazy GeminiProvider default
  - NEW app/services/ai/evals/__init__.py + fixtures/*.json (3 de-identified golden fixtures)
  - EDIT app/routers/consultation.py — removed _ai_client / get_ai_client() / google.genai imports; wired both endpoints through _ai_service; routers read ai_result.raw for unchanged HTTP response shapes
  - EDIT app/routers/letters.py — removed _ai_client / get_ai_client() / google.genai imports; wired draft_letter through _ai_service; route now properly async via the facade (was previously blocking the event loop directly)
  - NEW tests/test_ai_service_boundary.py — 14 tests using FakeProvider; no network, no DB, no live Gemini call
- Verification run:
  - py_compile on all 6 touched/new Python modules: OK
  - pytest tests/test_ai_service_boundary.py --noconftest -v: 14 passed in 1.16s (Python 3.11.7)
  - import boundary: grep app/ for google.genai -> only app/services/ai/providers/gemini.py
  - git diff --check: clean
- Remaining risks:
  - letters.py draft_letter was previously a blocking (non-awaited) genai call inside an async def; now properly non-blocking via asyncio.to_thread in the facade. Behaviour improvement, not a regression.
  - AiService() instantiated at module import time for both routers; genai.Client construction remains lazy (first actual call only) so import does not trigger credential resolution.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-ai-provider-boundary-facade.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
