# Ariadne CF-D2 workflow incident diagnosis and fluidity repair — final independent veto

## Binding

- Candidate: `6f28bb802ff15f63944ad4a968f04cc13bf0107a`
- Baseline: `d1e8d31e79d8af1f5e9fa4ea6b5e68f22aaa1e3b`
- Worktree: `C:/Users/sarashera/EMR4-worktrees/r190`
- Branch: `codex/cf-d2-workflow-fluidity-repair-gemini-review`
- Role: independent read-only verifier using Gemini 3.6 Flash/high.

Use only the bound clean worktree. Do not modify files, branches, refs or external
systems. Execute only the separately bound structured argv manifest, exactly in
order. Do not run a provider, database, Docker, product, network, credential,
deployment, Pages or protected-ref operation.

## What to examine

Determine whether the candidate accurately diagnoses why CF-D2 consumed roughly
four hours without reaching proof and whether the repair restores useful
improvisation without weakening hard authority, data, effect, stop, cleanup,
claim, identity or protected-ref controls.

In particular, inspect:

1. whether the diagnosis distinguishes genuine PostgreSQL/transaction complexity
   from workflow amplification and avoids claiming an unproved exclusive cause;
2. whether `orchestration/harness_settings/evidence_led_workflow.yaml` clearly
   separates hard controls from adaptive flow;
3. whether `scripts/ariadne_evidence_gate.py` mechanically rejects retries that
   cannot discriminate among viable hypotheses and rejects unbound or misleading
   verifier command evidence;
4. whether `scripts/ariadne_antigravity.py` admits a pass only when every exact
   manifest command is returned in order with exit code zero;
5. whether receipt event names are discoverable and exact Git candidate identities
   are machine-resolved and reverified;
6. whether the changes preserve compatibility for callers that do not supply a
   command manifest; and
7. whether tests and policy documents bind the intended behavior rather than only
   describing it.

The files in scope are the exact candidate diff from the bound baseline, with
primary attention to the plan, diagnosis, evidence-led policy, verifier policy,
three changed scripts, diagnostic packet/result, register revisions 253-254 and
their focused tests. Historical receipts in the diff are provenance, not a new
authority source.

## Decision contract

Return `revision_required` for any P0, P1 or P2 defect, any material overclaim,
any weakening of a hard boundary, any executable-path bypass, any mismatch between
the command manifest and reported results, any nonzero command result, or any
dirty/head/branch drift. Return `pass` only if no such issue remains.

The review must name all findings with severity and file/line evidence, or state
explicitly that no P0-P2 finding exists. It must also summarize the exact command
results, candidate HEAD, branch and clean post-state. This review accepts only the
workflow repair; it does not convert stopped CF-D2 into a pass and grants no new
database or product authority.
