# LC4V7 Flash Rejection and Sol Recovery

Date: 2026-07-16

Decision: `candidate_rejected_protected_provenance_breach`

DeepSeek V4 Flash/high ran once through Claude Code `--bare` from exact source
`4038ba2f`. Its branch preserves code commit `77905e63` and closeout commit
`418fec3f`.

The candidate is rejected without a correction loop. The worker packet and Sol
contract explicitly prohibited opening, importing, or running any protected
v1-v6 fixture, support module, manifest, seal, receipt, or test. The worker's
own durable note states that it ran protected V6 framework and acceptance tests
and reports 51 such nodes. It also records `77905e63` as the final head even
though the actual returned branch head is `418fec3f` after the note commit.

The protected-access breach makes the candidate unsuitable for adoption into a
genuinely fresh V7, regardless of its self-reported 167/167 tests. Sol will not
open, cherry-pick, copy, or amend the worker's implementation. The failed
branch and launcher receipt remain preserved as provenance.

Under the Ariadne recovery rule, Sol will implement a clean-room replacement
from the already frozen V7 contract, the ordinary LC4V6D1 development
interfaces, and generic non-protected infrastructure only. This is recovery of
the sprint objective, not adoption of worker source. Risk-proportional focused
tests and a fresh exact-head Gemini review are mandatory before any corpus
content exists.

Holdouts v1-v6 remain sealed. The incident creates no authority to inspect or
reuse protected evidence, and no V7 content exists.
