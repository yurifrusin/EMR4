# Bernie Synthetic Receptionist Silver Review Round 1 Disposition

Date: 2026-07-17

## Reviewed candidate

- Source: `0688818f3681da22a5586ce03f6a996eaa1f93e6`
- Canonical hash: `sha256:a7d2292adb4aca76c86fcdd019dc44d1708d9723a9b282db181327af889039bf`
- DeepSeek review commit: `8b70553b`
- Gemini review commit: `b52f2f7a`

Both independent reviewers mechanically and semantically reviewed all 192
records and returned `pass`, `accept=192`, `quarantine=0`, `reject=0`. Neither
reported protected or external-corpus access.

## Sol disposition

Sol did not admit that exact candidate. DeepSeek noted that eight one-shot
records declared `correction` although the correction could be implicit. A
complete Sol audit of every `correction` declaration found 18 records whose
dialogue contained no explicit correction surface. That conflicts with the
contract requirement that corrections be explicit and means the declared
noise metadata was not fully supported by the text.

The defect was bounded to `noise_operations`; dialogue, semantic anchors,
evidence spans, provenance, adjudication, and authority fields were unchanged.
Sol removed only the 18 unsupported `correction` labels, added a regression
test binding every remaining correction declaration to explicit text, and
regenerated the candidate set.

The first-round reviews remain valid historical evidence for the exact old
hash, but cannot accept or veto the revised hash. Fresh independent reviews
are required before admission.

DECISION: revision_required
REASON: unsupported_noise_operation_metadata
PROTECTED_ACCESS: false
EXTERNAL_CORPUS_ACCESS: false
