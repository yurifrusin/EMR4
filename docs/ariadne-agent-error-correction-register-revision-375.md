# Ariadne agent error and correction register — revision 375

Date: 2026-08-18

Timestamp: 2026-08-18T12:43:29+10:00 (Australia/Brisbane)

Status: accepted bounded containment

## Revision

Revision 375 adds AER-0427. The occupied DeepSeek V4 Flash/high worker exited
with launcher code 1 after returning no worker result or diagnostic stderr. Its
expected result artifact was absent, while the isolated branch remained clean
at exact frozen source `4daa2d772ffcf64e55f69917d2fb21802e959673`.

The non-result is preserved without a model-quality or provider-cause claim.
Because the same exit-1 signature has recurred and this attempt produced no
transferable work, no same-lane retry is used. Sol takes the unchanged frozen
route-adapter package under an explicit recovery lease; Gemini remains the
independent exact-candidate veto after deterministic admission.

## Population

- incidents: 427;
- corrected or explicitly contained: 427;
- open: 0;
- latest id: `AER-0427`.

No worker source, product route, database, provider fallback, deployment or
protected ref opened. The failed isolated branch is clean and excluded from
later adoption; protected refs remain unchanged.
