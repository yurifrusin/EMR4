# A5.1/B4.1 revision 3 pre-verifier state repair

Date: 2026-08-05

The first deterministic orchestration preflight for the revision 3 verifier
state returned `revision_required` before any verifier launch because the state
omitted the required `claude_cli_print` and `codex_subagent_spawn` adapter
observations. It made zero provider/model calls and conferred no dispatch
authority.

Sol added explicit no-assignment observations for both adapters without changing
the candidate, worktree, authority, data, provider, cost or review boundary. The
preflight was rerun and the committed receipt now returns `passed` with all five
named rehydration sources. Only then was the fresh Gemini verifier launched.
