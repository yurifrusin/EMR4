# Ariadne agent error and correction register — revision 368

Date: 2026-08-18

Timestamp: 2026-08-18T09:31:03+10:00 (Australia/Brisbane)

Status: accepted bounded containment

## Revision

Revision 368 adds AER-0419. The occupied DeepSeek V4 Flash/high worker exited
with launcher code 1 after returning no worker result or diagnostic stderr. Its
expected receipt and both owned files were absent, while the isolated branch
remained clean at exact frozen source
`2b20e59c4a6c6584709f794e7ed4b5e6b1dc5b0b`.

The non-result is preserved without a model-quality or provider-cause claim.
Because the same exit-1 signature has recurred and this attempt produced no
transferable work, no same-lane retry is used. Sol takes the unchanged frozen
two-file implementation package; Gemini remains the independent exact-candidate
veto after deterministic admission.

## Population

- incidents: 419;
- corrected or explicitly contained: 419;
- open: 0;
- latest id: `AER-0419`.

No worker source, product route, database, provider fallback, deployment or
protected ref opened. The task branch alone advanced to preserve dispatch
evidence before the failure; protected refs remain unchanged.
