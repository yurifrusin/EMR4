# S13 - Registered Envelope Authority — Completion

## Candidate Commit

```
6595bf78d9ce5fb855df1a011268b726937f8c5a
```

on branch `deepcode/s13-envelope-authority`.

## Changed Files (vs integration point `0d0b5a5f`)

| File | Change |
|---|---|
| `app/services/diary/envelope_capability_policy.py` | **New** — `validate_envelope_authority()` seam + `EnvelopeAuthorityDecision` dataclass. Pure domain logic: resolves action_name to grammar verb, looks up `capability_name` in `BERNIE_CAPABILITY_REGISTRY`, validates author against `allowed_authors`, validates envelope type vs capability tier. Unknown names pass through. |
| `app/services/diary/envelopes.py` | Lazy `model_validator` callbacks on `DiaryActionProposal`, `DiaryActionConfirmation`, `DiaryActionSuggestion` — import `validate_envelope_authority` inside the validator to avoid top-level cycle. |
| `app/services/diary/capability_manifest.py` | Updated capabilities `note` and `drift_watch` to describe registered-envelope enforcement accurately without claiming router/RBAC/live-command enforcement. |
| `app/services/diary/__init__.py` | Exports `EnvelopeAuthorityDecision` and `validate_envelope_authority`. |
| `tests/test_envelope_capability_policy.py` | **New** — 20 tests covering permitted/rejected authors, tier compatibility, unknown name passthrough, standalone function, import purity, and manifest posture. |

## Tests Run

```text
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_envelope_capability_policy.py tests/test_diary_action_envelopes.py tests/test_diary_action_boundary_contracts.py tests/test_bernie_diary_capability_manifest.py tests/test_diary_action_grammar.py -q
```

**Result:** All 112 tests passed (20 policy-specific + 92 broader envelope/manifest/grammar suite).

## Closed-Boundary Result

- **No routers, REST/OpenAPI, or GraphQL artifacts edited.** The policy seam is pure domain logic.
- **No schemas, models, or migrations touched.** Envelope models are test-only data classes with added validators; no schema/migration changes.
- **No provider code, UI/client code, deployment/release configuration edited.**
- **No confirm actions, routes, or terminal-to-active policy changed.** The policy enforces author/tier compatibility but does not add new write paths, confirm actions, endpoints, audit writes, provider calls, database access, or network calls.
- **No H15/H-series, historical-trove, memory/RAG/GraphRAG, or API-Spine command semantics touched.** Import purity test confirms no prohibited imports in `envelope_capability_policy.py`.
- **Enforcement is envelope-construction-time only.** Route-level author enforcement remains future work. Unknown free-string action names pass through without enforcement.

## Summary

All five task requirements are satisfied:

1. Policy seam `validate_envelope_authority()` looks up registered names in `BERNIE_CAPABILITY_REGISTRY` and validates author + envelope compatibility.
2. Applied to `DiaryActionProposal`, `DiaryActionConfirmation`, and `DiaryActionSuggestion` via lazy `model_validator` imports — no top-level import cycle.
3. Unauthorized author rejected; non-propose-tier registered names rejected in proposal envelopes; non-read-only/meta registered names rejected in suggestion envelopes; non-confirm-tier registered names rejected in confirmation envelopes.
4. Unknown free-string `action_name` values pass through without enforcement.
5. Manifest note and drift watch updated to accurately describe envelope-level enforcement without claiming router/RBAC/live-command enforcement.

STATUS: complete
