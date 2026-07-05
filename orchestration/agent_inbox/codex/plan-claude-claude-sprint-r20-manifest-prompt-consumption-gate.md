# plan-claude-claude-sprint-r20-manifest-prompt-consumption-gate

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-r20-manifest-prompt-consumption-gate` |
| Status | pending_plan_review |
| Created | 2026-07-05 21:39 +1000 |
| Source HEAD | `8631e6f` |

## Plan Summary

Add a safe, read-only manifest prompt-consumption gate: a pure helper that derives a compact, PHI-free, write-authority-free prompt context from the existing Bernie Diary Capability Manifest, plus deterministic safety tests. No live prompt is wired; this is a non-runtime scaffold ready for future Bernie prompt assembly.

## My Understanding

The full manifest already exists (app/services/diary/capability_manifest.py, MANIFEST_SCHEMA_VERSION bernie.diary_capability_manifest.v1) and has golden tests (tests/test_bernie_diary_capability_manifest.py) but currently has ZERO consumers. R20 asks for the first safe read-only CONSUMPTION gate: a way to expose compact manifest context toward future Bernie prompt assembly, provably without PHI, credentials, executable code, DB rows, or write authority, with deterministic tests. The manifest is source-derived from enums/registries only, so it is already structurally PHI-free; the gate must keep it that way, shrink it to a prompt-appropriate budget, and add an explicit safety guard so a future prompt path cannot smuggle unsafe content through it.

## Intended Surface / Boundary

Backend service layer only: app/services/diary/capability_manifest.py (new pure helpers) and a new test module. The consumption gate is a non-runtime scaffold. NO change to live Bernie prompts, no Gemini/provider calls, no interpreter/service.py wiring, no routes. Nothing user-visible: the diary grid, booking slots, cards, status colours, waiting-room panels, and Command Centre are untouched.

## Out Of Scope

Live Gemini calls or any provider invocation; changing production prompts or interpreter prompt assembly; wiring the context into app/services/bernie/interpreter.py or ai/service.py; DB migrations; frontend/Diary UI changes; raw codebase/manifest dumping into a prompt; PHI or log ingestion; autonomous writes; RBAC changes; modifying the existing manifest golden output shape.

## Files I Expect To Edit

app/services/diary/capability_manifest.py (add build_manifest_prompt_context(), render_manifest_prompt_block(), a MANIFEST_PROMPT_CONTEXT_MAX_CHARS budget, and an assert_manifest_prompt_safe()/redaction guard; extend __all__); tests/test_bernie_manifest_prompt_consumption.py (new deterministic safety tests). Orchestration: only this task packet's Completion Notes during the plan gate.

## Implementation Steps

1) Add build_manifest_prompt_context(): a pure function that calls build_bernie_diary_capability_manifest() and projects it to a compact, prompt-appropriate subset — schema_version, authority_statement, principles, key entity value lists (statuses/channels/reason codes), session states, capability tiers/authors and names-only rows (drop verbose per-item summaries if over budget), the confirmation envelope_sequence write-authority flags, and the non_authority_boundaries. Drop long notes/drift_watch prose. Keep it JSON-serializable and deterministic (sorted). 2) Add MANIFEST_PROMPT_CONTEXT_MAX_CHARS budget constant and enforce/verify the compact size. 3) Add assert_manifest_prompt_safe(payload): a defensive gate that scans the serialized payload for forbidden markers (credential/token/secret/password/api_key keys, patient-identifier-shaped fields like medicare/dob/phone/first_name/last_name/address, and any writes_authorized:true outside the declared confirmation-boundary description) and raises ValueError if found; build_manifest_prompt_context() runs this gate before returning. 4) Add render_manifest_prompt_block(context=None) -> str: a deterministic, human/model-readable text rendering of the safe context for future prompt assembly, still carrying the read-only authority statement; does not call any model. 5) Extend __all__. 6) Write deterministic tests. 7) Run py_compile + focused pytest.

## Visual / Behavioural Acceptance Checks

Behavioural only (no UI): (a) build_manifest_prompt_context() returns a dict that json.dumps round-trips; (b) its serialized length is <= MANIFEST_PROMPT_CONTEXT_MAX_CHARS and materially smaller than the full manifest; (c) no PHI/credential markers anywhere in the payload (case-insensitive scan); (d) the only writes_authorized:true appears in the confirmation-boundary sequence entry and is clearly labelled staff-confirmation-required; (e) render_manifest_prompt_block() is a str containing the read-only authority statement and is stable across calls; (f) assert_manifest_prompt_safe() raises on a deliberately poisoned payload (injected fake medicare/secret) and passes on the real one; (g) existing manifest golden tests still pass unchanged; (h) no route/prompt is invoked — grep shows no new provider/model call.

## Risks / Ambiguities

1) Ambiguity: R20 allows wiring into an existing safe assembly point 'only if one exists' — none does today, so I deliberately build a non-runtime scaffold and do NOT wire it, which is the safer merge per merge criteria; flag for Ariadne if she wants live wiring instead. 2) Redaction guard is heuristic (keyword-based); it is a defence-in-depth net, not a proof — the primary guarantee is that the manifest is source-derived from enums only. 3) Char budget is a judgement call; I will pick a generous constant and assert relative shrink rather than a brittle absolute. 4) Keeping the full-manifest golden shape unchanged so no existing test breaks.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
