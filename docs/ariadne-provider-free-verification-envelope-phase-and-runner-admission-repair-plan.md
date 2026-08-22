# Ariadne provider-free verification-envelope phase and runner-admission repair plan

Date: 2026-08-23

Timestamp: 2026-08-23T05:30:28.8721970+10:00 (Australia/Brisbane)

Status: `frozen`

Planning source HEAD:
`9a1cbe5b0b0679378da841f9521f815abd7cd348`

Accepted predecessor closeout source:
`a33a4ccc7619fcae5cdd45a48a2312ab0c0384a4`

Protected source:
`2e34bdad732fdab32fbf778280b3d3c70d66d602`

Operation:
`ariadne-provider-free-verification-envelope-phase-and-runner-admission-repair`

Target result:
`ariadne_provider_free_verification_envelope_phase_and_runner_admission_repair_pass`

Reasoning level: High. This is a bounded deterministic workflow-control repair
with no product, database, provider or protected-ref effect.

## Starting fact and authority

The accepted predecessor retired its two product-harness failure coordinates,
but AER-1024 and AER-1026 proved that the surrounding verification process
still admitted two avoidable manual choices:

1. a database-closed tranche could be tested through ordinary or serial pytest,
   which loads repository `tests/conftest.py`; and
2. a live-projection test could be selected before the clockwork publication
   whose projection it was meant to verify.

The six database-bearing results and the prepublication Baton mismatch are
excluded. This tranche adds no evidence about a database or attempt 008.

## Narrow objective

Create one typed verification-envelope semantic gear and project it into the
two existing command-control surfaces:

- verifier command manifests executed by `scripts.ariadne_validation_runner`;
  and
- clockwork governance command manifests validated before generation
  construction.

The gear owns exactly two finite fields:

- `database_authority`: `closed` or `open`; and
- `verification_phase`: `prepublication` or `postpublication`.

When database authority is `closed`, direct pytest and
`scripts.ariadne_serial_pytest` are structurally rejected before subprocess
launch. The only admitted pytest entry point is
`scripts.ariadne_provider_free_pytest`. Non-pytest deterministic commands remain
eligible. A manifest's phases must be monotonic: no prepublication command may
appear after a postpublication command.

## Frozen implementation shape

### Shared semantic gear

A small provider-free module owns exact database-authority and phase
vocabularies, Python-module/pytest-runner classification, database-closed
runner admission and monotonic phase validation. Both existing manifest
validators call it; neither keeps a parallel free-form interpretation.

### Verifier command-manifest v2

The existing v1 verifier manifest remains accepted only for immutable
historical compatibility. Opt-in v2 adds manifest-level
`database_authority` and command-level `verification_phase`.

The validation runner must:

- validate the complete v2 manifest before any command runs;
- require one explicit phase for v2 execution;
- execute only commands carrying that exact phase;
- retain the full manifest digest plus selected phase and database authority in
  its durable receipt;
- preserve stop-on-first-failure and digest-only stdout/stderr evidence; and
- continue to bind provider-free test selections to the exact repository and
  no-database admission digest.

Missing, unknown or reordered phases, a missing execution phase, direct pytest
and serial pytest under closed authority all reject before `subprocess.run`.

### Governance command-manifest v2

The existing clockwork v1 command manifest remains readable for historical
generation replay. Opt-in governance v2 adds the same manifest-level authority
and command-level phase fields and calls the same semantic gear.

The clockwork must reject an invalid v2 manifest before generation
construction, canonical mutation or publication. The closeout for this tranche
must itself use v2 with database authority `closed`, a prepublication provider-
free gate and a postpublication provider-free projection gate.

## Allowed files and evidence

The tranche may change only:

- one shared verification-envelope semantic module;
- the existing evidence-gate, validation-runner and governance-clockwork
  validators;
- focused tests for those surfaces;
- this plan and threat-model delta;
- a bounded contract/schema, deterministic conformance evidence/report and
  focused plan tests;
- required register, acceptance, Continuity, Compass, latch, closeout and Yuri
  artifacts through the clockwork closeout path.

No existing test may be run through ordinary or serial pytest during this
tranche. All repository tests use the already accepted provider-free runner.
Pure subprocess behavior is exercised only with fakes or newly authored
temporary Python commands that have no repository conftest or database path.

## Acceptance

Acceptance requires all of the following:

1. a passed fresh five-source receipt with explicit DeepSeek, Gemini and native-
   subagent dispositions;
2. exact ancestry of the accepted predecessor and preservation of all four
   protected refs;
3. one shared finite vocabulary and runner classifier consumed by both
   existing control surfaces;
4. backward-compatible v1 read admission and exact v2 closed-authority/phase
   admission;
5. pre-launch rejection of direct and serial pytest under closed authority;
6. exact provider-free pytest admission, repository-bound selection digest and
   no child launch on hostile manifests;
7. explicit phase required for v2 execution, phase-only command selection,
   monotonic phase order and durable phase/authority receipt fields;
8. clockwork rejection of hostile v2 manifests before generation construction
   and successful dry-run/publication of this tranche's typed v2 closeout;
9. focused and broader provider-free tests, Ruff, Python compilation, JSON/
   schema readback and `git diff --check` passing;
10. zero conftest, engine, schema, fixture, Docker, PostgreSQL, SQL, database,
    provider, worker, product or attempt-008 execution; and
11. clockwork-only canonical closeout, paired lay/technical Yuri summary,
    usual non-PHI Pushover, explicit-path staging and preservation of
    `docs/branding/` plus every unrelated untracked file.

## Parallelism assessment

- **DeepSeek native Harness:** `declined`, negative leverage. The latch forbids
  a worker/provider call and this is a local deterministic control-plane gear.
- **Gemini:** `declined`, neutral leverage. No provider call is authorised and
  hostile schema/process-fake tests decide the complete bounded contract.
- **Native subagents:** `declined`, negative leverage. Developer policy forbids
  proactive delegation and both projections share one serial semantic module.
- **GPT Sol:** owns plan, implementation, verification, acceptance, clockwork
  and Git closeout.

## Claim and continuation boundary

This repair can prove only that typed manifests reject the two observed
verification-envelope mistakes before child execution and that requested phases
select their own commands. It cannot prove database, product, provider or
attempt-008 behavior.

No database conftest/engine/schema/fixture, Docker, PostgreSQL, SQL, attempt 008,
DeepSeek/Gemini/provider call, application/product/API/OpenAPI/GraphQL/route/
client/configuration change, ordinary-practice enablement, feature flag,
allowlist, grammar, generic-status `Arrived`, waiting-area movement, patient/
clinical/historical/protected data, production, deployment, release, Pages or
protected-ref movement is authorised. Local/origin `master` and
`handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

After this gear passes, a fresh successor may decide whether the repaired
deterministic admission is sufficient to freeze an attempt-008 plan. This
tranche does not make that decision and cannot execute an occupied attempt.
