# plan-claude-claude-ai-provider-boundary-facade

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-ai-provider-boundary-facade` |
| Status | integrated |
| Created | 2026-06-26 15:06 +1000 |
| Source HEAD | `f5ea0e7` |

## Plan Summary

Add a thin backend-only EMR4-owned AI service boundary (app/services/ai) that wraps the three existing Gemini call sites (consultation analysis, audio scribe, letter drafting) behind EMR4 capability contracts and one Gemini adapter. Routers call the facade via a raw passthrough so runtime behaviour is byte-for-byte unchanged, and a fake-provider test proves structured-output validation without any live Gemini call.

## My Understanding

orchestration/ai_provider_boundary.md already ratifies the direction: keep Gemini first-class but stop letting provider SDK calls define EMR4 internal contracts; providers are adapters behind EMR4 clinical/reception contracts. Today google.genai is imported and called directly from routers in two duplicated places: consultation.py (analyze-consultation text->JSON and scribe-consultation audio+text->JSON) and letters.py (letters/draft text->JSON). All three use genai.Client(vertexai=True), model gemini-2.5-flash, GenerateContentConfig(response_mime_type=application/json, temperature 0.1/0.3), then json.loads(response.text) read with .get() defaults. The boundary must be incremental and must not spread provider SDK imports into new surfaces.

## Intended Surface / Boundary

Backend only. New package app/services/ai is the only place importing google.genai going forward. Capabilities exposed by the facade: clinical_extraction, audio_scribe, letter_drafting. Behaviour-preservation contract: the facade returns a result carrying .raw (the exact json.loads(response.text) dict as today) AND .data (a permissive validated contract model); routers keep using .raw so returned JSON, prompts, model, temperature, and _saved/error paths are unchanged. Validation is introduced and covered by tests on .data without being able to reject real Gemini output. Surfaces that MUST NOT change: the prompt text, gemini-2.5-flash, temperatures, response_mime_type, HTTP response shapes of all three endpoints, the audio file save path/audio_url, MBS Discovery Engine search (_search_mbs_rules), diary frontend, taskpane, Command Centre, migrations, Bernie runtime.

## Out Of Scope

Provider switch, LiteLLM/OpenAI gateway, prompt rewrites, live Gemini credential/eval runs, splitting the audio-scribe pipeline, diary/taskpane/Command Centre UI, Bernie runtime, migrations, any change to consultation/letter clinical behaviour. No production code edits before complete sprint task.

## Files I Expect To Edit

NEW app/services/ai/__init__.py; NEW app/services/ai/contracts.py (capability enum + permissive Pydantic request/response models with extra=allow and optional fields mirroring current .get() defaults, plus AiResult wrapper raw+data); NEW app/services/ai/providers/__init__.py; NEW app/services/ai/providers/gemini.py (single home for lazy genai.Client(vertexai=True), model name, GenerateContentConfig, json.loads(response.text); GeminiProvider.generate_json(contents, temperature); small AiProvider Protocol for fake injection); NEW app/services/ai/service.py (AiService facade: analyze_consultation_text, scribe_audio, draft_letter; builds contents, calls provider via asyncio.to_thread as today, parses once, validates, returns AiResult); EDIT app/routers/consultation.py (replace two inline generate_content blocks with facade calls, keep reading .raw); EDIT app/routers/letters.py (replace inline block with facade call, read .raw); NEW app/services/ai/evals/fixtures/*.json (2-3 small de-identified goldens, one per capability); NEW tests/test_ai_service_boundary.py (fake provider returns fixtures, no network).

## Implementation Steps

1. Create app/services/ai/ package with AiProvider Protocol and AiResult/contract models in contracts.py. 2. Implement GeminiProvider moving existing client construction + call config verbatim (same vertexai/project/location, model, config). 3. Implement AiService facade reproducing each current call contents and temperature; parse once; build raw + validated data. 4. Rewire consultation.py (both endpoints) and letters.py to use GeminiProvider via the facade and read .raw, preserving every surrounding line (logging, _save_encounter, _saved, audio save, exception messages, asyncio.to_thread). 5. Add fixtures + tests/test_ai_service_boundary.py using a fake provider. 6. Run verification.

## Visual / Behavioural Acceptance Checks

analyze-consultation, scribe-consultation, letters/draft return identical JSON shapes and error strings as before (verified via .raw and existing tests if present). The only module importing google.genai is app/services/ai/providers/gemini.py. New tests pass with no live provider call; facade validation tolerates extra and missing fields. py_compile clean on touched modules; git diff --check clean.

## Risks / Ambiguities

Strict validation could change behaviour -> mitigated by permissive contracts (extra=allow, optional fields) and routers reading .raw not .data. Two duplicate get_ai_client() defs: consolidating into the adapter is the point; confirm no other module imports either before removing. Dead-scaffold risk: a boundary nothing calls would not reduce coupling, so recommend wiring all three call sites now via low-risk raw passthrough; if Codex prefers scaffold-only with no router edits that is a smaller even-safer variant (flagging for review). asyncio.to_thread must be preserved for the blocking Vertex calls (known event-loop-freeze hardened fix).

## Codex Plan Review

- Review result: Accepted; scope is backend-only and matches the AI boundary strategy.
- Required changes before implementation: None.
- Approved to proceed: yes
