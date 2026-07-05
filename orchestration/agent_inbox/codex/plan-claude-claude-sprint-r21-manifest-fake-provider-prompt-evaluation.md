# plan-claude-claude-sprint-r21-manifest-fake-provider-prompt-evaluation

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-r21-manifest-fake-provider-prompt-evaluation` |
| Status | pending_plan_review |
| Created | 2026-07-05 22:02 +1000 |
| Source HEAD | `84b4c23` |

## Plan Summary

Fake-provider-only evaluation harness proving the Bernie manifest prompt block grants no write authority, leaks no PHI, and cannot bypass backend confirmation; no live Gemini calls.

## My Understanding

R20 landed build_manifest_prompt_context()/render_manifest_prompt_block() in app/services/diary/capability_manifest.py (compact, PHI-free, write-safe scaffolds guarded by assert_manifest_prompt_safe). Nothing consumes them via a model yet. R21 adds a fake-provider-only evaluation seam: assemble the manifest prompt block plus adversarial receptionist instructions, feed a scripted fake provider satisfying the existing AiProvider protocol, and prove deterministically that schema literacy grants no write authority, leaks no PHI, and cannot bypass confirmation. No live Gemini/Vertex calls; must be CI-safe and must NOT wire live Bernie prompt consumption.

## Intended Surface / Boundary

New non-runtime module app/services/diary/manifest_prompt_eval.py (harness + fake provider + adversarial scenarios) and new tests. Reuses AiProvider protocol from app/services/ai/contracts.py and R20 manifest functions via read-only imports; no runtime change to capability_manifest.py. Not touched: diary grid, booking slot/card/status UI, waiting room, taskpane, Command Centre, any live prompt-assembly path, and the real GeminiProvider.

## Out Of Scope

Live Gemini/Vertex calls; production/live Bernie prompt wiring; frontend/Diary UI; DB migrations; raw appointment mutations; PHI/log ingestion; broad AI provider refactor; changing R20 manifest content or char budget.

## Files I Expect To Edit

app/services/diary/manifest_prompt_eval.py (new); tests/test_bernie_manifest_fake_provider_eval.py (new); optional short orchestration doc note only, no runtime doc edits.

## Implementation Steps

1) FakeManifestPromptProvider implementing AiProvider.generate_json returning scripted deterministic dicts, recording calls, no I/O, never given real credentials. 2) assemble_manifest_eval_prompt(scenario)=render_manifest_prompt_block()+delimited receptionist-instruction section; deterministic. 3) evaluate_manifest_prompt_block(provider,scenarios) applies deterministic invariants independent of fake response: no write-authority leak (assert_manifest_prompt_safe + only confirmation envelope writes_authorized), no PHI (no _FORBIDDEN_KEY_PATTERNS markers; PHI-exfil scenario still shows non-authority boundary), no confirmation bypass (block keeps 'cannot authorize writes'/'only confirmation authorizes writes' statements), and flags a poisoned fake response claiming write authority. 4) Return typed JSON-serialisable deterministic ManifestPromptEvalReport. 5) Tests cover determinism, isinstance AiProvider, no network/DB, all adversarial scenarios uphold invariants, evaluator flags poisoned response, prompt contains authority statement.

## Visual / Behavioural Acceptance Checks

No visual surface changes (backend/test only). pytest tests/test_bernie_manifest_fake_provider_eval.py -q passes with zero network/DB/provider calls; py_compile clean; existing R20 tests/test_bernie_manifest_prompt_consumption.py still passes; git diff --check clean.

## Risks / Ambiguities

'Fake-provider' could be read as touching app/services/ai/ — mitigated by keeping the fake provider local to the diary eval module and only importing the AiProvider protocol. Risk of implying live wiring — mitigated by module docstring plus a test asserting no live client path is exercised. Evaluator invariants are heuristic/structural (consistent with R20 defence-in-depth); authoritative guarantee remains that the manifest is enum/registry-derived, stated in code comments so it is not mistaken for RBAC.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
