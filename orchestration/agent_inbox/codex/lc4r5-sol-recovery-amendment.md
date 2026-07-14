# LC4R5 Sol Recovery/Adoption Amendment

Date: 2026-07-14

Recovery and integration owner: GPT Sol.

## Candidate provenance

DeepSeek V4 Flash/high through Claude Code `--bare` produced worker commit
`dc5c69fd142bd2318101b49beae374ee6dade7a1` on
`codex/lc4r5-dw1-explanation`. The hardened launcher bound the process cwd,
`PWD`, `INIT_CWD`, and packet authorization root to the disposable worktree.
Protected master was observed clean immediately before launch, repeatedly
during the lane, and after completion. The worker branch was clean after its
commit.

The compact launcher receipt returned `status: completed` and ended with
`DECISION: pass`. It records one denied attempt to use PowerShell
`Set-Content` inside the disposable worktree. The worker then used permitted
tools, removed its temporary construction helpers, committed only the six
owned files, and did not write to protected master.

## Evidence deficiency and Sol disposition

The worker completion artifact correctly names its model, transport, branch,
scope, counts, hashes, and test commands, but its `Candidate Commit` section
omits the literal hash required by the packet. The durable launcher receipt
and Git branch independently establish the source commit above. Sol preserves
the worker artifact unchanged so its omission is not hidden, and owns this
amendment as the authoritative provenance reconciliation.

No worker closeout claim is transferred to Sol. Sol adopts the commit only as
an untrusted runtime candidate under the Ariadne recovery lease and owns all
subsequent verification, acceptance, and integration decisions.

## Sol review and adoption

Sol reviewed the full diff from planning base
`820bc594f89d6fdb7b25906cfb02fa61bf00385a` and confirmed:

- the runtime change is confined to the `explain_schedule` clarification
  branch and adds resolved practitioner context without broadening action
  detection;
- existing patient-specific behavior remains supported;
- the authored tests cover resolved, corrected, ambiguous, omitted,
  anti-overmatch, safety, negation, time, lossless normalization, oracle
  independence, and tool boundaries;
- the report uses only the development loader and observed surface-derived
  action/entity semantics; and
- no fixture, generator, scenario schema, audit/scorer policy, action grammar,
  provider, route, database, UI, T3 gate, deployment, historical-diary, or
  protected-evidence surface changed.

Sol independently reran 148 focused semantic and LC4R4 report tests, the
LC4R5 `--check`, and diff hygiene successfully before adopting the worker
commit on protected master as
`426eade96c11eef3b50ce94755927b19eda78b68`.

Acceptance remains pending broader deterministic verification and Gemini 3.5
Flash independent veto review of the exact recovered head.
