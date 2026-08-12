# Ariadne CF-D2 workflow-incident diagnosis and fluidity-repair plan

Date: 2026-08-12

Status: `frozen_repository_only_implementation_authorised`

Planning baseline HEAD:
`d1e8d31e79d8af1f5e9fa4ea6b5e68f22aaa1e3b`

## Objective

Diagnose why CF-D2 consumed roughly three and a half hours of active commit
windows across two bounded sequences without reaching its first crash, then
repair the workflow so hard safety controls remain exact while diagnostic and
review work becomes more evidence-led, discoverable and fluid.

This is a workflow tranche, not a CF-D2 recovery. It must not identify an
unsupported database root cause, reopen attempt 003 or authorize another
database run.

## Inputs and outputs

Inputs are tracked ordinary repository artifacts only: the CF-D2 plans,
contracts, harness source, tests, immutable authored-synthetic failure
evidence, receipts, review packets, stop closeouts, Git chronology, Ariadne
policies and incident register.

Outputs are:

1. an evidence-backed incident diagnosis that distinguishes technical
   complexity from workflow amplification;
2. one machine-readable evidence-led workflow policy;
3. a pure deterministic diagnostic-decision and command-manifest gate;
4. discoverable receipt-event vocabulary from the receipt CLI;
5. optional structured command-manifest admission in the Antigravity verifier
   transport; and
6. focused tests, final independent veto, closeout and paired Yuri summary.

## Hard controls that do not change

- five-source rehydration at the configured continuation events;
- explicit authority, data, provider, side-effect, stop, cleanup and claim
  boundaries at tranche entry;
- sealed protected evidence and real-data restrictions;
- immutable failed attempt evidence and exact cleanup;
- default denial, no silent fallback and no failure-to-success relabelling;
- serial shared-PostgreSQL tests;
- exact candidate/ref/worktree binding, explicit-path staging and protected-ref
  closure; and
- one fresh independent veto when the risk policy triggers it.

## Fluidity repairs

### One boundary, one final veto

The tranche uses one active plan/contract and one final risk-triggered external
review. It does not add separate external planning, formatting-recovery and
implementation ceremonies when deterministic checks can decide those states.
A new receipt is required for a configured continuation event, not for every
internal thought or prose revision inside the same unchanged event.

### Discriminate before correcting

A participant coordinate is not an internal assertion. Before a correction is
called the cause, a structured hypothesis set must leave exactly one viable
cause. When several causes remain, a diagnostic may proceed only if each has a
distinct observable outcome. A necessary defect may be corrected while causes
remain only when the next bounded observation distinguishes every remaining
hypothesis; otherwise the workflow stops or changes direction before spending
the correction and runtime allowance.

### Executable review evidence

External-review commands are structured argv arrays with stable IDs. Shell
wrappers and compound command strings are rejected. Python files under
`scripts/` are invoked as modules. A review result must reproduce the exact
manifest in order, and a `pass` is inadmissible if any command exit code is
nonzero. This removes prose comparison and prevents a later successful command
from masking an earlier failure.

### Discoverable vocabulary

The receipt CLI exposes the exact configured continuation-event vocabulary.
Agents do not guess event names from phase prose. AER-0285 preserves the final
pre-repair recurrence that used intuitive `pre_plan` instead of configured
`pre_sprint_planning`.

## Acceptance

- The diagnosis is explicit that workflow structure amplified delay but did
  not prove the unresolved PostgreSQL anchor cause.
- The policy identifies hard controls and adaptive flow separately.
- The diagnostic gate rejects exclusive-cause claims with multiple viable
  hypotheses and rejects corrections that cannot create a distinct next
  observation.
- The command gate rejects direct `scripts/*.py` execution, shell compound
  commands, command substitution/widening/reordering and `pass` with any
  nonzero command.
- The receipt CLI lists the configured vocabulary without requiring a runtime
  state.
- Existing no-manifest Antigravity behaviour remains compatible; manifest-
  bound reviews fail closed and record the manifest digest and exact results.
- Focused tests, Ruff, compilation, canonical fast verification and Git
  whitespace pass.
- One fresh exact-HEAD Gemini 3.6 Flash/high read-only veto reports zero P0–P2
  findings and an unchanged clean candidate.

## Recovery and stop

Implementation is Sol-owned and repository-only. Deterministic failures are
repaired locally without external dispatch. The final verifier receives one
fresh attempt; a transport failure may use the configured bounded retry, but a
substantive rejection stops this tranche for evidence-backed repair rather
than opening nested review ceremonies.

## Closed surfaces and claim boundary

No Docker or database runtime, CF-D2 attempt, key rotation, retention/purge,
operational database/source or watcher, protected evidence, `docs/branding/`,
unrelated untracked file, provider, patient/clinical/product data,
credentials/IAM, executable product tool or command, deployment, production,
release, Pages or protected-ref movement is authorised.

A pass proves only that the revised Ariadne workflow mechanically preserves
hard gates while preventing the four diagnosed classes of process drift. It
does not prove CF-D2, identify its remaining anchor cause or authorize another
durability tranche.
