# Ariadne CF-D2 workflow incident diagnosis and fluidity repair closeout

Date: 2026-08-12

Result: `ariadne_cf_d2_workflow_incident_diagnosis_and_fluidity_repair_pass`

Reviewed source: `018099dd6c5f0502121360732feb602252eb34cc`

## Outcome

The workflow diagnosis and repair pass. CF-D2 does not.

CF-D2 contained real PostgreSQL and transaction-state complexity, but the
workflow amplified it. Across the two active work windows it produced 19
commits and a diff dominated by 87 orchestration packet/receipt files and 23
documents while changing only two source scripts. The decisive structural
error was treating isolation of a participant coordinate as isolation of one
internal assertion: several viable anchor failures collapsed into the same
nonzero/null-SQLSTATE envelope, yet a correction was spent without a distinct
next observation for each remaining hypothesis.

The hard controls worked. Default denial stopped unsafe continuation; no third
runtime attempt, crash, restart, provider/product operation or protected-ref
change occurred; immutable evidence and exact cleanup were preserved. The
repair therefore keeps those controls and removes ceremony where deterministic
local evidence can decide the state.

## Accepted repair

- `orchestration/harness_settings/evidence_led_workflow.yaml` separates hard
  authority/data/effect/stop/cleanup/claim controls from adaptive flow.
- `scripts/ariadne_evidence_gate.py` rejects unsupported exclusive-cause
  claims, nondiscriminating retries, shell-wrapped/compound review commands,
  direct repository-script execution and a pass with any command drift or
  nonzero exit.
- `scripts/ariadne_orchestrator_preflight.py` makes configured continuation
  events discoverable rather than memorable.
- `scripts/ariadne_antigravity.py` binds a structured command manifest, uses a
  provider-admissible response shape and admits results only after exact local
  ID/argv/order/exit-code comparison.
- Git candidate identities must come literally from `git rev-parse` and be
  reverified in the review worktree.
- One active boundary and one final risk-triggered veto replace repeated
  external planning, formatting and implementation ceremonies when local
  checks are sufficient.

The retrospective CF-D2 diagnostic packet returns
`revision_required/correction_would_not_create_discriminating_evidence` because
four viable anchor hypotheses share the same observation. Under the repaired
workflow, the insufficient correction and second database attempt would not
have been admitted.

## Verification

Fresh Gemini 3.6 Flash/high review of exact source
`018099dd6c5f0502121360732feb602252eb34cc` reported no P0-P2 finding. Its
schema-constrained receipt is bound to command-manifest SHA-256
`eacd8fe2a40e0445c5936449a55915f21be0c251ae1b60f7cf907dd41ff9e332`.
All nine exact commands returned zero: 46 focused workflow tests, 228 register
tests, Ruff check and format, Python compilation, Git whitespace and clean
pre/post state. HEAD and branch were unchanged. The final repository canonical
fast profile also passed Ruff, in-memory compilation of 202 maintained source
files, 191 focused API Spine/handover/receipt/maintenance tests, Diary JavaScript
syntax and Git whitespace.

The first dispatch was intentionally not erased. Local preflight rejected one
invalid runtime-state vocabulary/inventory pair before dispatch (AER-0287).
The following fresh project reached the provider but stopped at HTTP 400
schema admission because tuple-only `prefixItems` lacked the provider-required
array `items` field (AER-0288); no review or command resulted. The provider-
admissible repair retained stronger exactness at the deterministic local gate.
AER-0285 through AER-0288 are closed at register revision 255.

## Claim and authority boundary

This pass proves a repository workflow repair, not the remaining PostgreSQL
anchor cause. CF-D2 attempt 003 remains ineligible; no crash/restart or unknown-
commit claim is released. Key rotation and retention/purge remain dependency-
blocked.

No database/Docker runtime, operational source/watcher, real/product/patient/
clinical data, provider product call, credential/IAM operation, executable
product tool or command, reusable runtime, deployment, production, release,
Pages or protected-ref movement is opened. `docs/branding/` and all unrelated
untracked files remain preserved and excluded.

## Next programme decision

There is no dependency-satisfied automatic durability tranche after this
closeout. Starting another CF-D2 descendant would contradict the new evidence
gate, while key rotation and retention/purge require CF-D2. The next useful
step is therefore a genuine Yuri-owned programme fork: select a separately
valuable product/architecture direction, or explicitly commission a new
observability-first CF-D2 architecture with new authority. No further tranche
starts implicitly from this result.
