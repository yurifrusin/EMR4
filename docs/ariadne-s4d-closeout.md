# Ariadne S4d Closeout

Date: 2026-07-11
Outcome: passed with reduced independent review

S4d exercised the Ariadne role split on real EMR4 harness work. Claude Opus at
medium reasoning performed the actual Conductor calls in this sprint. Deep Code
verified the corrected allocation and the PTY adapter dispatched three bounded
DeepSeek Flash worker lanes. GPT Sol remained the protected orchestrator and
sole integrator/committer/pusher.

The sprint exposed and corrected several real failures:

- stale worktrees and incomplete settings fingerprints;
- Deep Code's real-TTY requirement and non-terminating `-p` sessions;
- additive permission settings that repeatedly prompted for approved writes;
- Windows notify-hook execution failure;
- contradictory and fabricated worker closeout claims;
- a D3 ownership breach; and
- an over-rigid rule that allowed failed worker closeouts to deadlock progress.

The resulting PTY adapter automates project settings, permission refusal,
artifact freshness, turn completion, bounded cleanup, process confirmation,
untrusted completion events, and receipts without preserving terminal output.
Four historical stale Deep Code processes were removed.

Yuri approved provenance-preserving recovery leases. Worker attestations remain
non-transferable, but the orchestrator may adopt source as untrusted candidate
material, amend it under its own identity, preserve failures, and close low-risk
work through deterministic tests and diff review. High-risk recovery still
requires independent verification.

The active orchestrator identity was corrected from stale GPT Terra wording to
stable resource `openai-primary-orchestrator`, current model GPT Sol. Future
Conductor preference is Claude Fable first, Claude Opus only for Fable usage or
availability failure, then a distinct spawned GPT Sol subagent with no
integration authority.

D2 was accepted normally. D1 and D3 candidate source was recovered by GPT Sol;
no failed worker closeout was rewritten as worker evidence, and D3's unowned
edit was excluded. Seventy focused tests pass at settings fingerprint
`sha256:14b8ae3439d6ce03bb1c4405dd42694acc62ca1fd4278f0812c480b57e7e775c`.
The PTY npm dependency audit reports zero vulnerabilities.

Antigravity/Gemini 3.5 Flash returned no veto decision and was stood down. The
bounded Ariadne-local fallback passed, with reduced independence and residual
risks recorded in
`orchestration/agent_inbox/codex/review-ariadne-local-s4d-veto-fallback.md`.

S4d changes only harness code, settings, documentation, tests, fixtures, and
evidence. It opens no EMR4 runtime, provider, frontend, database, GraphQL,
H-series, D5, deployment, release, or production authority.
