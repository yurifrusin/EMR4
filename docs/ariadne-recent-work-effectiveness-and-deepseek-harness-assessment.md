# Ariadne recent-work effectiveness and DeepSeek Harness assessment

Date: 2026-08-17

Timestamp: 2026-08-17T10:01:53.2381516+10:00 (Australia/Brisbane)

Status: `deterministic_candidate_admitted_pending_independent_veto`

Source HEAD: `38660a4a7136094df67b28d5a6ec07ca40c14416`

DeepSeek Harness source: `47f943859bef60e4160492346772ded9b24f765a`

## Executive conclusion

Yuri's impression is supported, with an important qualification. Recent
tranches contain real engineering complexity and the hard safety controls have
prevented false acceptance. The recurring inefficiency is concentrated after a
candidate becomes semantically credible: Git identities, command/test
envelopes, lifecycle result capture and duplicated closeout evidence have
created a long verification-and-publication tail.

This does not support cutting the final veto, database cleanup, authority
checks or acceptance claims. It supports making their inputs machine-derived
and their execution durable. The three implemented controls do exactly that:
machine Git/ref snapshots, a one-command durable validation runner with pytest
admission, and DeepSeek worker environment hardening.

The effectiveness findings below were derived from EMR4 evidence before and
independently of the DeepSeek Harness comparison. DeepSeek Harness was then
used as a source of possible mechanisms, not as the explanation for the
observed delays.

## Part A — independent review of recent EMR4 work

### Evidence method and limits

The review used committed plan, candidate and closeout timestamps; CF-D2's
accepted incident diagnosis; the risk-weighted reform closeout; the latest
delete-confirm closeout; and AER-0369 through AER-0378. Commit spans are an
operational proxy, not a time sheet: they can contain provider latency, user
conversation, compaction, deliberate pauses and uncommitted work. They support
directional conclusions, not a precise productivity percentage.

The nine most recent comparable spans were:

| Tranche | Plan-to-closeout | Candidate-to-closeout tail |
|---|---:|---:|
| risk-weighted workflow reform | 83.8 min | 38.5 min |
| delete-confirm catalogue rehearsal | 63.4 min | 18.9 min |
| delete-confirm behaviour rehearsal | 191.4 min | 38.8 min |
| route convergence review | 45.5 min | 25.8 min |
| response/product-adapter architecture | 155.2 min | 118.1 min |
| unmounted product adapter | 173.6 min | 77.2 min |
| route-mounting readiness | 159.0 min | 96.6 min |
| HTTP route convergence | 127.5 min | 23.9 min |
| HTTP/PostgreSQL integration | 142.3 min | 22.1 min |

The median candidate-to-closeout tail was 38.5 minutes. The tails totalled
459.9 of 1,141.7 sampled minutes, or 40.3%. That ratio must not be labelled
waste: it includes final verification and accurate closeout. It does establish
that closeout is a large enough phase to warrant direct optimization.

### What is necessary

- exact authority, data, effect, cleanup and claim boundaries;
- exact candidate and protected-ref binding;
- serial database tests and owned disposable-runtime cleanup;
- one risk-triggered independent veto;
- immutable failure evidence where a rejected run could otherwise be mistaken
  for acceptance; and
- paired lay/technical reporting that prevents later architectural drift.

The latest HTTP/PostgreSQL tranche found two substantive cross-seam defects:
incomplete signed delete evidence and missing transaction-local tenant
context. Catching those defects was not ceremony.

### What is avoidable

AER-0370 and AER-0376 record invented full hashes from displayed prefixes.
AER-0372 records a compound command whose later successes masked an earlier
failure. AER-0378 records four excluded pytest runs with the wrong conftest or
serialization envelope. AER-0373 records stale baton assertions. AER-0374,
AER-0375 and AER-0377 record repeated helper/profile/probe-shape repairs.
AER-0371 records a worker installing dependencies into the primary `.venv`.

CF-D2 is the stronger historical signal: about three and a half active hours,
19 commits, 87 agent-inbox files, 23 documents, 12 continuity files, eight test
files and two source scripts accumulated before the runtime reached its first
planned `SIGKILL`. That diagnosis already concluded that Ariadne was formal in
the wrong place: it governed permission precisely but did not require the next
observation to discriminate among the remaining causes.

### Judgment

Yes, some closeouts have taken longer than is optimal. The repository does not
support the stronger claim that they are uniformly twice as long as necessary,
or that one exact percentage can be removed. It supports a narrower claim:
manual evidence transcription and non-durable validation have repeatedly
consumed a material minority of several tranche tails without increasing
semantic assurance.

The operating target is therefore not “less checking.” It is one exact
candidate, one durable deterministic run, one final risk-triggered veto, and a
machine-populated closeout spine. After several further tranches, compare the
same timing measure and recurrence signatures. For ordinary non-occupied
tranches, a median candidate-to-closeout tail below 25 minutes is a useful
directional target; database/provider tranches remain complexity-adjusted.

## Part B — DeepSeek Harness assessment

### What it is

At the reviewed source, DeepSeek Harness is an MIT-licensed developer preview
whose own README warns of rapid breaking change. It is a Cordis/plugin-oriented
agent harness with explicit workflow/session abstractions, event logging,
model adapters and optional subagent providers.

The strongest portable ideas are:

- configuration captured as an immutable operation input;
- paired workflow/session begin and terminal events;
- model-visible events being observable rather than hidden in transport glue;
- holder-owned runs with explicit cancellation/disposal; and
- fail-loud behavior when a capability or provider is not configured.

These resemble Ariadne's direction but are implementation patterns, not proof
that the Harness meets EMR4's protected-evidence, authority or clinical safety
requirements.

### Authentication and migration finding

The primary `llm-pi-ai` adapter explicitly does not provide an OAuth credential
store, OAuth login flow or refresh lifecycle, and identifies `openai-codex` as
an OAuth-only route it cannot presently offer. Supplying a manually extracted
token would be short-lived and would not create subscription-backed conductor
operation.

The separate Codex subagent provider can launch `codex app-server --stdio` and
reuse the host Codex installation's authentication. It is still a one-shot
subagent beneath a separately funded parent model: it does not give the parent
Harness access to the ChatGPT subscription, inherit the parent's full context,
resume a Codex thread, stream progress, provide a human approval path or roll
back side effects.

Migration is therefore rejected now for four independent reasons:

1. the existing ChatGPT subscription cannot fund the Harness conductor;
2. the project is explicitly a breaking developer preview;
3. Ariadne's protected evidence, latch, receipts, exact-worktree review and
   integration controls would require a substantial port; and
4. migration would introduce a second orchestration debugging surface while
   EMR4 is returning to product work.

Codex remains conductor. DeepSeek remains a bounded implementation worker
through the existing Claude Code `--bare` lane; Gemini remains the independent
veto lane.

Primary sources:

- `https://github.com/deepseek-ai/DeepSeek-Harness`
- `https://github.com/deepseek-ai/DeepSeek-Harness/blob/master/docs/architecture.md`
- `https://github.com/deepseek-ai/DeepSeek-Harness/blob/master/docs/subsystems/workflow.md`
- `https://github.com/deepseek-ai/DeepSeek-Harness/blob/master/packages/llm/llm-pi-ai/README.md`
- `https://github.com/deepseek-ai/DeepSeek-Harness/blob/master/packages/subagent/subagent-codex/README.md`

## Part C — adaptations implemented in Ariadne

1. Orchestrator receipts now include a fixed read-only Git snapshot populated
   directly from the repository: HEAD, current branch and origin, all four
   protected refs, tracked cleanliness, untracked count and `docs/branding/`
   presence. Protected-ref mismatch returns `revision_required`.
2. `scripts.ariadne_validation_runner` admits the existing structured argv
   manifest, writes an atomic `in_progress` receipt before execution, updates
   it after every command, stops on the first failure and stores only output
   digests and byte counts. Direct pytest is rejected; serial/provider-free
   launchers and exact existing test paths are enforced.
3. The DeepSeek-via-Claude environment removes inherited virtualenv/Python and
   package-index targeting, sets pip/uv/npm/yarn offline or noninteractive
   controls, and carries an explicit no-install/no-environment-mutation
   instruction. This is defence in depth, not hostile-process containment.

No DeepSeek Harness package, source or dependency was installed, copied or
executed. No Raisa product behavior or protected ref changed.
