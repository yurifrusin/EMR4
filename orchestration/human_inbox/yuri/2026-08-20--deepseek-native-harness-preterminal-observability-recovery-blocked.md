# DeepSeek Harness observability recovery — blocked handover

Date: 2026-08-20

## Lay summary

The repair work is behaving well: it now records exactly how far a future
DeepSeek Harness boot gets, instead of collapsing several possible early
failures into one vague error. All 168 relevant local checks pass, and no
DeepSeek process or provider call was made during this repair.

I have not called the tranche complete. The first Gemini review missed an
incorrect test-count statement in its instructions, and the corrected reviews
are currently being refused by Antigravity with a 403 permission error. After
three identical predecision failures I stopped retrying. Please restore or
reauthorise Gemini 3.7 Flash/high inference in Antigravity; no code needs to be
rebuilt and the candidate can then receive one fresh corrected review.

## Technical summary

- Candidate: `b5f0bc0d823a1c8009f3bb49efcc9a588b9703ab`.
- Deterministic result: 10/10 scenario matrix, exact runner SHA-256
  `230d5a2d41f3768260fb908bd1d7e162cdd102cb32867cfa3d4a69e9fe376a5e`,
  exact timing-envelope SHA-256
  `057392e7156907504165cbe6a74e50e78550ff9452b60467660087ee9fad4345`.
- Tests: exact reviewer suite 85/85; expanded owned/neighboring/latch/clockwork/
  baton-consistency suite 168/168; Ruff and compile pass.
- Review attempt 1: provider `pass`, orchestrator `revision_required` because
  the packet falsely asserted 137 tests rather than 85.
- Corrected review transports: three attempts, zero admitted decisions, each
  clean and HEAD-stable; local Antigravity terminal diagnosis is HTTP 403
  `PERMISSION_DENIED`.
- Separate inherited signal: the optional acceptance-index test still rejects
  the pre-existing 121,619-byte `AGENTS.md` against its 80,000-byte budget.
- Boundaries: zero native Harness/agent/broker/model/provider/network/Docker/
  database operations; no product or protected-ref changes; 654 unrelated
  untracked entries and all five `docs/branding/` entries preserved.
- Non-PHI Pushover notification succeeded with request
  `b9345ed1-688c-4b46-bedd-23f75385e976`.
