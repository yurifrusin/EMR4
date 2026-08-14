# Ariadne agent error and correction register — revision 270

Date: 2026-08-14

Timestamp: 2026-08-14T23:17:51+10:00 (Australia/Brisbane)

Revision 270 records AER-0309. The register now contains 309 bounded known
incidents, all corrected or contained by an explicit control.

AER-0309 records a bounded DeepSeek egress-contract defect. The implementation
packet required exactly one JSON object and no prose, but the otherwise
completed result placed the requested object after two prose sentences and
inside a Markdown code fence.

The mismatch does not validate or invalidate the source candidate. Sol treats
the worker narrative as non-authoritative, inspected the exact one-file commit
`db5292d8eb07caf3ba4b7e31ab72233b14c91288`, and independently reran Ruff plus
the 109-test combined update/API Spine packet in the clean disposable worktree.
Those direct results, Git state and later independent review—not the worker's
self-description—control admission.

The added control requires output-schema instructions and transport receipts to
be checked separately. A parseable object embedded in extra prose is still an
output-contract violation; its candidate may proceed only on independently
reproduced deterministic evidence and normal review.
