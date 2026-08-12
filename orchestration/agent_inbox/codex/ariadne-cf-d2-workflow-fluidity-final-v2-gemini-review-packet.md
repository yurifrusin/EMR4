# Ariadne CF-D2 workflow incident diagnosis and fluidity repair — final veto retry

## Binding

- Candidate: `018099dd6c5f0502121360732feb602252eb34cc`
- Baseline: `d1e8d31e79d8af1f5e9fa4ea6b5e68f22aaa1e3b`
- Worktree: `C:/Users/sarashera/EMR4-worktrees/r190`
- Branch: `codex/cf-d2-workflow-fluidity-repair-gemini-review`
- Role: independent read-only verifier using a fresh Gemini 3.6 Flash/high conversation.

The first conversation ended at provider tool-schema admission with HTTP 400
because `command_results` had tuple-only `prefixItems` and no provider-required
`items`. It produced no review, executed none of the manifest commands and left
the candidate clean. Treat that event only as immutable transport evidence. Do
not reuse any conclusion or state from it.

Use only the bound clean worktree. Do not modify files, branches, refs or external
systems. Execute only the separately bound structured argv manifest, exactly in
order. Do not run a database, Docker, product, provider tool, credential,
deployment, Pages or protected-ref operation.

## What to examine

Determine whether the candidate accurately diagnoses why CF-D2 consumed roughly
four hours without reaching proof and whether the repair restores useful
improvisation without weakening hard authority, data, effect, stop, cleanup,
claim, identity or protected-ref controls.

Examine whether:

1. the diagnosis distinguishes genuine PostgreSQL/transaction complexity from
   workflow amplification without claiming an unproved exclusive cause;
2. the evidence-led policy clearly separates hard controls from adaptive flow;
3. the evidence gate rejects retries that cannot discriminate among viable
   hypotheses and rejects substituted, reordered or falsely successful commands;
4. the Antigravity wrapper's provider-facing uniform `items` schema is admissible
   while exact command ID, argv, order and zero-exit enforcement remains local;
5. receipt event names and exact Git candidate identities are discoverable and
   machine-resolved; and
6. callers without a command manifest remain compatible.

Primary scope is the exact candidate diff from the bound baseline: the plan,
diagnosis, evidence-led and verifier policies, three changed scripts, diagnostic
packet/result, register revisions 253-255, dispatch evidence and focused tests.

## Decision contract

Return `revision_required` for any P0, P1 or P2 defect, material overclaim,
weakened hard boundary, executable-path bypass, command-result mismatch, nonzero
command exit, or dirty/head/branch drift. Return `pass` only if no such issue
remains. Name findings with severity and file/line evidence, or state explicitly
that no P0-P2 finding exists. Summarize all nine command results, exact HEAD,
branch and clean post-state. A pass accepts only this workflow repair; CF-D2
remains stopped and unproved and no database or product authority is granted.
