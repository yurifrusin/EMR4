# Governance clockwork bound closeout entrypoint and explicit-stage manifest rehearsal — plan

Date: 2026-08-23

Timestamp: 2026-08-23T21:18:20.9899474+10:00 (Australia/Brisbane)

Status: `frozen`

Operation:
`ariadne-provider-free-governance-clockwork-bound-closeout-entrypoint-and-explicit-stage-manifest-rehearsal`

## Purpose

Turn the accepted clockwork cadence map into one deterministic closeout
control. The control selects and attests the repository virtual-environment
interpreter, executes the existing semantic commands, captures the live-state
reading returned inline by a successful publication, retains the complete
postpublication test selection and emits an exact allowlisted stage manifest.

The occupied rehearsal uses only the nonpublishing path. It may prove the
publication-result capture path with injected local results, but it must not
publish a live semantic generation, invoke `git add` or mutate the Git index.

## Owned implementation

- `scripts/ariadne_governance_clockwork_closeout.py`;
- the narrow verification-only mode in
  `scripts/ariadne_governance_clockwork_tick.py`;
- the semantic command profile in
  `orchestration_harness/governance_clockwork_tick.py` only to lint the new
  driver;
- focused tests in `tests/test_ariadne_governance_clockwork_tick.py`;
- this plan, its threat delta, exact provider-free evidence, report, efficacy
  reading, closeout, acceptance, receipts and Yuri summary; and
- canonical clockwork surfaces only through the established writer at final
  closeout, never through the new driver during this rehearsal.

No product, route, API, client, configuration or runtime source is owned.

## Frozen driver contract

1. The caller supplies only a repository-local semantic closeout intent and an
   explicit mode. The driver machine-resolves the repository root, full
   40-character HEAD and virtual-environment interpreter.
2. Interpreter attestation must prove the child reports the exact resolved
   repository interpreter. No environment variable, credential or secret is
   read or changed.
3. Rehearsal invokes the existing tick through a new `--verify` mode. That mode
   admits the same semantic intent, executes the same three semantic command
   rows, builds the same prospective generation in memory and reports zero
   publication and zero pointer movement.
4. The live path may invoke the existing `--publish` command, but no live-path
   invocation is authorised in this tranche. Tests must prove that the driver
   accepts only a passing publication result whose transaction facts show one
   committed generation and binds the returned source, generation, lease and
   status as the inline live validation reading.
5. After either accepted command result, the driver runs the unchanged
   postpublication selection: Current Baton, active latch, governance
   clockwork, transactional closeout and orchestrator preflight tests through
   the repository interpreter and provider-free serial runner.
6. The driver compares tracked status across the postpublication tests and
   rejects test-created drift.
7. The explicit-stage allowlist is derived from the admitted intent,
   contract-owned canonical/metadata paths and fixed driver outputs. The
   manifest intersects that allowlist with machine-read Git changes, rejects
   every unexpected tracked path, excludes unrelated untracked paths and
   records zero index mutations and zero `git add` invocations.
8. Driver outputs have fixed names beside the intent:
   `closeout-driver-result.json` and `explicit-stage-manifest.json`. The caller
   does not transcribe their paths.

## Rehearsal sequence

1. Commit the frozen plan and implementation candidate with explicit paths.
2. Invoke the new driver in rehearsal mode from a non-repository Python
   launcher if useful; verify its child is the repository interpreter.
3. Require all three semantic commands and the complete postpublication suite
   to pass, with no live publication or index change.
4. Inspect the emitted stage manifest against Git status and confirm
   `docs/branding/` plus every unrelated untracked path is absent.
5. Run focused and combined governance verification, Ruff and diff checks.
6. Close through the established clockwork writer, not the new driver, then
   rerun the retained postpublication suite.

## Acceptance

The tranche passes only if:

1. repository interpreter selection and child attestation are deterministic;
2. system-Python launch cannot cause semantic `active_interpreter_mismatch`;
3. rehearsal executes all semantic command rows with zero publication;
4. tests prove exact inline publication-result capture and rejection of
   malformed, dry-run or idempotent substitutes;
5. the unchanged five-file postpublication selection runs after the tick
   result and detects any tracked drift;
6. the manifest contains only changed, existing, repository-relative,
   allowlisted explicit paths, includes its own fixed output path and excludes
   `docs/branding/`;
7. no code path invokes `git add`, writes the index or silently stages;
8. focused tests, the retained semantic and postpublication suites, Ruff,
   JSON validation, latch validation, protected-ref checks and
   `git diff --check` pass; and
9. no provider, worker, product/data source, production runtime, deployment,
   release, Pages, protected evidence or protected ref is opened.

## Parallelism assessment

- **DeepSeek:** declined. The native occupied profile remains paused and the
  new driver is precisely the serial orchestrator control boundary, not an
  owned worker package. Claude Code is not a fallback.
- **Gemini:** declined. Interpreter, subprocess, Git-path and transaction
  invariants have deterministic executable tests and no semantic veto surface.
- **Native subagents:** declined under developer policy and because one serial
  closeout sequence owns the mutation boundary.
- **Owner:** GPT Sol.

Reassess only if deterministic evidence conflicts, the live publisher contract
must change materially or an external verifier becomes an explicit acceptance
requirement.

## Claim boundary

Passing proves a provider-free driver rehearsal and a no-index stage manifest.
It does not yet adopt the driver for live publication, reduce tests, stage
files automatically, qualify the native DeepSeek Harness or open any product,
data, provider, runtime, deployment, release, Pages or protected-ref surface.
