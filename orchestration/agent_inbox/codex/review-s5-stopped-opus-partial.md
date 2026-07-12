# S5 Stopped Opus Partial Evidence

Date: 2026-07-12

The user explicitly stopped the mechanical Opus fingerprint-refresh invocation.
The process was terminated, but inspection later found an uncommitted partial
edit in the Claude worktree. It changed only the claimed Conductor resource,
fallback explanation, settings fingerprint, drift note, and workspace HEAD in
`plan-claude-fable-s5-d1-continuation-v2.md`.

The partial edit is rejected and non-authoritative because:

- the invocation was stopped by the user;
- its fallback was triggered by an orchestrator-imposed monetary cap that was
  not user-approved;
- the current cost-control policy prohibits that fallback trigger;
- its fingerprint predates the committed cost-control settings; and
- it was never committed or verified.

No D-1 scope, worker allocation, repair authority, or EMR4 code was changed.
The Claude worktree may restore the committed plan before Fable refreshes it
against the current baton.
