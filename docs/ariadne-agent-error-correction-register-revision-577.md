# Ariadne agent error and correction register — revision 577

Date: 2026-08-20

<!-- ariadne-agent-error-register-reading
revision: 577
incident_count: 724
new_incident_ids: AER-0716,AER-0717,AER-0718,AER-0719,AER-0720,AER-0721,AER-0722,AER-0723,AER-0724
open_incident_count: 0
-->

This revision records nine bounded workflow and implementation incidents exposed
while building the provider-disabled pre-HMR startup terminal. No DeepSeek,
Gemini or provider request occurred. One overly broad legacy test selection
briefly started the local test broker through its provider-free ready-only path;
it terminated in the test cleanup and exact process readback is zero. All six
incidents are contained and none remains open.

## AER-0716 — the first continuation receipt used a recalled event alias

The runtime state supplied `pre_plan`, while the orchestrator schema owns the
exact `pre_sprint_planning` continuation event. Preflight rejected before any
source change or dispatch.

Correction: the configured event vocabulary was listed and the corrected
five-source preplanning receipt passed with `pre_sprint_planning`.

## AER-0717 — post-compaction Git evidence repeated machine-owned object IDs

The first post-compaction runtime state again put exact Git object IDs in
hand-authored `git_refs_and_worktree` prose. The machine-snapshot guard rejected
the receipt before implementation resumed.

Correction: the narrative now delegates every exact ref identity to the
machine-generated snapshot. This is a recurrence of the already guarded
AER-0709 pattern, and both rejected receipts remain preserved.

## AER-0718 — timeout validation initially required a text signature

The first pure terminal implementation treated `hmr_bootstrap_failed` only as
a signature-derived cause, so its exact `native_worker_timeout` coordinate with
no matched text group failed its own validator.

Correction: relationship validation now distinguishes exact controller facts
from nonzero-exit text classification and the focused timeout fixture passes.

## AER-0719 — the evidence runner initially omitted direct-script bootstrapping

The new evidence script imported repository packages before adding the
repository root to `sys.path`, so two direct `python script.py` invocations
failed locally before building evidence.

Correction: the script now performs the standard bounded repository-root
bootstrap before local imports and both `--build` and `--check` pass.

## AER-0720 — an ordering probe retained a pre-refactor source fragment

After stream reads were made per-label and failure-preserving, the deterministic
source-order probe still searched for the earlier literal stdout call. The
evidence build and two tests rejected before acceptance.

Correction: the probe binds the stable per-label assignment seam and all five
ordering assertions now pass.

## AER-0721 — an overly broad legacy test selection started the local broker

The first combined focused run included the full historical controller test
file, whose ready-contract regression starts one local test broker. That was
outside this tranche's zero-broker boundary even though it made no provider
request and terminated in `finally`.

Correction: exact process readback confirms zero matching broker processes and
the accepted validation manifest now runs only the provider-disabled recovery
suite, which monkeypatches both `Popen` and `run` to fail if invoked.

## AER-0722 — the first closeout command omitted the module launcher

The first clockwork closeout check supplied the evidence runner as a direct
script path, while the clockwork command schema requires every Python command
to begin with `-m`. The check rejected before canonical mutation.

Correction: the command now uses the exact module path after `-m`; the
idempotent closeout intent otherwise remains unchanged.

## AER-0723 — the second closeout draft supplied untyped contract paths

The second clockwork check represented `contract_evidence` as four bare paths,
while continuity graph nodes require typed contract objects with an identifier,
status and evidence list. Prospective validation rejected before mutation.

Correction: schema inspection established that nonempty entries must be typed;
AER-0724 records the subsequent finding that this tranche has no registered
global contract and therefore requires an empty cross-node contract list.

## AER-0724 — the typed correction invented an unregistered global contract

The third clockwork check correctly rejected the local tranche contract as an
unknown global continuity contract ID and also rejected its paths because they
were not evidence for a registered cross-node contract.

Correction: `contract_evidence` is empty, matching the parent closeout and this
node's lack of a global cross-node contract. The local contract and schema paths
remain ordinary findings and artifacts.
