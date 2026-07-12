# EMR4 S6 Diary Contract Repair Closeout

Date: 2026-07-13
Status: complete, pending publication-state receipt

S6 restored the diary browser suite from eight known failures to a clean
139-test signal. The initial test-only plan was amended after Sol proved four
signed-confirm failures were caused by a production `ReferenceError`, not test
drift alone.

## Integrated Repair

- `saveBooking()` now derives a nullable AHPRA value only after practitioner
  validation, using known practitioner/template mappings and never treating a
  directory UUID as an AHPRA number.
- The diary JavaScript cache key advanced from v182 to v183.
- Practitioner-directory browser tests now model default-on GraphQL POST,
  exact variables, approved projection, sensitive-field exclusion, HTTP 401
  token clearing, 200-row rendering, REST fallback non-use, and smoke isolation.
- Existing signed create/update-confirm network assertions remain unchanged.

## Agent Evidence

- Claude Fable/Opus were unavailable because the shared subscription hit a real
  session limit.
- DeepSeek 4 Pro/high successfully served as fallback Conductor through Deep
  Code and amended S6 when Sol surfaced the runtime scope delta.
- DeepSeek Flash Lane 1 implemented and revised the candidate. Sol rejected the
  first weakening attempt and two incomplete revisions before accepting the
  final bounded diff.
- Corrected DeepSeek Flash Lane 2 static review returned PASS after Sol proved
  the candidate was present and persisted deterministic test evidence.
- Two invalid Lane 2 attempts are quarantined under
  `orchestration/archives/s6-invalid-review-attempt/` and cannot be acceptance
  evidence.

## Verification

- `review/test_diary_smoke.py`: 139 collected, 139 passed, exit 0.
- `node --check docs/diary/diary.js`: passed.
- `scripts/check_frontend_versions.py`: passed; diary.js v183.
- `tests/test_sprint_closeout_protocol.py` plus
  `tests/test_ariadne_deepcode_pty.py`: 21 passed.
- `git diff --check origin/master...HEAD`: clean before closeout edits.

A wider five-module Ariadne test run produced 47 passes and six failures. All
six are stale assertions in `tests/test_ariadne_deepcode_adapter_settings.py`
that still require exactly two DeepCode resources, Flash defaults for every
resource, and no Pro default. They predate the approved
`deepseek-pro-conductor-fallback`; S7 must reconcile those tests and audit the
associated settings contract.

## S7 Audit Seeds

1. Artifact-kind/packet marker mismatch (`VERDICT` versus required `DECISION`).
2. Candidate cherry-pick executed in the wrong worktree because command cwd was
   implicit; the first Lane 2 PASS was invalidated.
3. Strict DeepCode policy prompts on shell commands classified `unknown` or as
   outside-worktree reads; deterministic Sol execution plus static LLM review
   was used without relaxing security.
4. Worker scratch logs escaped declared output naming but were not integrated.
5. Adapter-settings tests drifted from the approved Pro conductor resource.
6. Worker artifacts misstated test counts despite successful execution; Sol
   collection remained authoritative.

No S6 work opened Bernie D5, provider, memory/RAG, historical diary runtime,
backend/database, deployment, external-client, schema, or new write-authority
gates. Terminal-status product policy remains deferred.

Sprint engine state: continuing automatically to S7 contract audit.
