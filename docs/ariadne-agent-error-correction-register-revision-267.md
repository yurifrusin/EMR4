# Ariadne agent error and correction register — revision 267

Date: 2026-08-14

Timestamp: 2026-08-14T09:37:51+10:00 (Australia/Brisbane)

Revision 267 records AER-0305. The register now contains 305 bounded known
incidents, all corrected.

AER-0305 records an exact test-count underreport in the dispatched Gemini
packet. The packet named the correct six test modules but predicted 35 tests.
Gemini ran all six and reported 51 passed. Fresh Sol `--collect-only` readback
in the unchanged review worktree confirmed exact per-file counts `9, 5, 8, 1,
6, 22`, totalling 51.

The packet remains immutable evidence of the error. No intended path was
missing, every collected item passed, and the verifier worktree stayed clean
at the exact candidate. Acceptance uses 51 and requires future exact packet
counts to come from the packet command's mechanical collection rather than
manual arithmetic.

No protected output, prompt, secret, credential, patient, clinical, document or
product-derived value is retained in this revision or its sanitized receipt.
