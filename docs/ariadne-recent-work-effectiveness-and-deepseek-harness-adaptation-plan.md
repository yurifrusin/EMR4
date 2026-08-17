# Ariadne recent-work effectiveness and DeepSeek Harness adaptation plan

Date: 2026-08-17

Timestamp: 2026-08-17T09:47:18.3542784+10:00 (Australia/Brisbane)

Source HEAD: `38660a4a7136094df67b28d5a6ec07ca40c14416`

Status: `deterministic_candidate_extended_by_blocked-state-guard_pending_independent_veto`

Reasoning level: workflow architecture and execution admission / Extra High

## Purpose

Review the last product tranches against the accepted CF-D2 and risk-weighted
workflow reforms, assess DeepSeek Harness from exact public primary source
`47f943859bef60e4160492346772ded9b24f765a`, decide adaptation versus conductor
migration, and implement only the smallest repeatable repairs supported by the
evidence.

This tranche changes Ariadne development orchestration only. It changes no
Raisa product source, API, database, migration, runtime, UI or clinical
meaning.

## Findings frozen before implementation

The completed delete-confirm HTTP/PostgreSQL tranche was materially complex:
it crossed route canonicalization, signed proposal ingress, authenticated RLS,
one atomic database command, public/private replay, rollback and disposable
runtime cleanup. That complexity explains part, but not all, of its elapsed
time. AER-0370, AER-0372, AER-0374, AER-0376 and AER-0378 show preventable
workflow friction around manually transcribed Git identities, compound command
execution, re-declared helper configuration and ambiguous pytest envelopes.
AER-0371 separately shows that a bounded worker could mutate the primary Python
environment despite an isolated Git worktree.

DeepSeek Harness is a substantial MIT-licensed developer preview with rapidly
breaking compatibility. Its current primary model adapter cannot use an
OAuth-only provider: it has no OAuth credential store or login/refresh flow,
and its own documentation names `openai-codex` as the installed OAuth-only
route. Its separate Codex subagent provider can launch the native Codex CLI and
inherit that product's authentication, but it is one-shot delegation beneath a
different parent model, not ChatGPT-subscription funding of the Harness
conductor. Migration is therefore rejected for the present programme on
entitlement, maturity, switching-cost and protected-evidence-integration
grounds. Codex remains conductor.

Portable mechanisms are admitted only where they answer observed Ariadne
failures: immutable per-run configuration snapshots, durable paired lifecycle
outcomes, fail-loud misuse and bounded ownership/cleanup.

## Exact repairs

1. Add a read-only machine-generated Git/ref/worktree snapshot to every
   orchestrator receipt. It must resolve `HEAD`, current branch, its local and
   origin ref when available, protected local/origin `master` and
   `handoff/current`, tracked cleanliness, untracked count and preserved
   `docs/branding/` presence. Protected-ref mismatch fails closed. Runtime prose
   remains contextual evidence but no longer needs manually transcribed object
   IDs.
2. Add a local structured validation runner over the existing exact argv
   command-manifest contract. It executes one shell-free command at a time,
   stops on first nonzero exit, atomically persists an immutable-config
   lifecycle receipt before and after each command, records only exit status,
   elapsed time and output digests/byte counts, and leaves full output in the
   live terminal. Direct pytest is rejected: repository tests must select the
   serial-conftest or provider-free launcher. The serial launcher rejects
   `--noconftest`, compound tokens and missing/out-of-root selected test paths.
3. Harden the DeepSeek-via-Claude worker environment and instruction packet:
   remove inherited virtual-environment and package-index targeting, force pip
   offline/no-input behavior, and explicitly forbid package-manager or shared
   environment mutation. This is defence in depth, not an OS sandbox claim.
4. A blocked, paused, complete or replaced active-operation latch must never
   emit worker-dispatch permission merely because the receipt otherwise
   validates. Dispatch additionally requires exact `in_progress` state and no
   user-attention condition.

The first repair addresses AER-0370/AER-0376. The second addresses AER-0372,
AER-0378 and the post-closeout terminal-result loss. The third addresses the
observed AER-0371 path. A shared Docker-profile type is deferred: the current
delete-confirm harness now validates its complete inherited argv before
occupied execution, and introducing a cross-family abstraction in this review
would create more coupling than it removes.

The fourth repair was admitted under continuous harness self-correction after
the exhausted verifier-transport receipt exposed AER-0381. It prevents a
terminal latch state from authorising another worker while the independent
veto remains unsatisfied.

## Exact implementation allowlist

- `orchestration_harness/git_refs_snapshot.py`;
- `scripts/ariadne_orchestrator_preflight.py`;
- `tests/test_ariadne_git_refs_snapshot.py`;
- `tests/test_ariadne_orchestrator_preflight.py`;
- `scripts/ariadne_validation_runner.py`;
- `tests/test_ariadne_validation_runner.py`;
- `scripts/ariadne_serial_pytest.py`;
- `tests/test_ariadne_serial_pytest.py`;
- `scripts/ariadne_deepseek_claude.py`;
- `tests/test_ariadne_deepseek_claude.py`;
- `orchestration/harness_settings/orchestrator_requirements.yaml`;
- `orchestration/harness_settings/evidence_led_workflow.yaml`;
- `orchestration/harness_settings/verifier_execution_policy.yaml`;
- this plan, its threat delta, assessment, receipts, error-register artifacts,
  Continuity/Compass updates, closeout, Sol acceptance, Yuri summary, AGENTS
  and exact tests for those artifacts.

No dependency install or vendoring from DeepSeek Harness is authorised.

## Verification and acceptance

Acceptance requires exact primary-source citations and commit binding; focused
tests for all three repairs including hostile inputs; proof that a protected
ref mismatch, manual/direct pytest, `--noconftest`, nonexistent test path,
compound command, command failure and interrupted receipt state fail closed;
Ruff, maintained-source compilation and Git whitespace checks; the current
risk-weighted canonical maintenance profile once; and one fresh Gemini 3.7
Flash/high exact-candidate veto with an unchanged clean review worktree.

## Parallelism and worker economy

Sol owns primary-source synthesis, frozen semantics, implementation integration
and acceptance. DeepSeek Flash is declined for implementation: the three
changes touch the worker launcher and shared receipt/test admission itself, so
briefing, isolating and recovering a worker would cost more than the bounded
serial implementation and would exercise the not-yet-hardened path under
review. Gemini 3.7 Flash/high is planned for exactly one final independent
veto. Native subagents are declined by current developer policy. Reassess only
if implementation reveals a separable mechanical package larger than its
dispatch overhead.

## Closed surfaces and next work

No product/patient/clinical/historical/protected data, provider product call,
ADC, credential/IAM mutation, external package install, database, Docker,
browser, product tool/command, deployment, production, release, Pages or
protected-ref movement is opened. Preserve `docs/branding/` and every unrelated
untracked file; stage explicit paths only.

After acceptance, return to the next dependency-satisfied Reception One
direction under Yuri's standing authority unless the accepted baton identifies
a narrower prerequisite.
