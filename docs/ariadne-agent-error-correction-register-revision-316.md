# Ariadne agent error and correction register — revision 316

Date: 2026-08-17

Timestamp: 2026-08-17T03:26:21.8618234+10:00 (Australia/Brisbane)

## Result

Revision 316 preserves 365 bounded known incidents. AER-0364 and AER-0365 are
corrected; no incident is open or contained.

AER-0364 records the first DeepSeek readiness-review candidate's omission of
the mandatory report timestamp. Sol caught the omission before admission. The
single permitted mechanical correction added the frozen ISO timestamp to the
deterministic renderer, regenerated the report and added an adjacent Date /
Timestamp assertion. The corrected five-output candidate then passed the exact
provider-free profile and fresh Gemini 3.7 Flash/high veto without changing the
7/5/0 readiness result.

AER-0365 records the first pre-verifier runtime sentence naming a tree object
ID in the field reserved for commit-ref evidence. The AER-0363 local
commit-resolution guard returned `revision_required` before any model call.
The failed receipt is preserved; the corrected v2 evidence names exact commit
HEAD only and passed before verifier dispatch. The guard worked as designed,
so no additional harness mechanism was needed.

## Boundary

These are bounded workflow observations and corrections, not model/provider or
product-quality claims. No route, schema, API Spine behavior, database,
capability, product data, provider fallback, deployment, Pages or protected
ref was opened.
