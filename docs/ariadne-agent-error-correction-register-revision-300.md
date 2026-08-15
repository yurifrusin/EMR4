# Ariadne agent error and correction register — revision 300

Date: 2026-08-15

Timestamp: 2026-08-15T22:21:45+10:00 (Australia/Brisbane)

Revision 300 records AER-0339. The register now contains 339 bounded known
incidents, all corrected or contained by an explicit control.

AER-0339 preserves Sol's omission of the canonical fast profile at exact plan
source `d500f1f86a83695cee0c2aac93aa2e2735e8f799` before worker dispatch. The
profile was first run on candidate
`bc0b8adcdc9f1c11bb69abe1514677a92d17f9c7` and exposed four failures.

The failures have two distinct causes. One dependency assertion is
candidate-caused because it did not yet admit the additive
`authority_generation` field. The other three are stale current-baton
assertions already failing at the exact plan source after the accepted Ariadne
harness closeout. None is admitted as a product failure and the candidate
remains revision-required.

The correction binds each affected test narrowly to its demonstrated cause,
reruns every correction separately, then reruns the complete canonical fast
profile before candidate admission. Future worker plans must execute and record
that complete profile at the exact source before dispatch so source drift and
candidate causation cannot be conflated.
