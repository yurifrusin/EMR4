# Ariadne agent error and correction register — revision 415

Date: 2026-08-18

Status: incomplete correction attempt

Reasoning level: high

Revision 415 preserves accepted revision 414 and adds AER-0485. Immediately
after the clean pre-dispatch receipt, the orchestrator repeated the corrected
command-scope defect by piping `rg --files` into a second `rg` process. The
violation was detected before any worker worktree, container or provider call.

The correction stops pre-dispatch work, requires one executable with its own
native filtering arguments, and extends the complete register suite. This
revision was not accepted: its cross-attempt `related_incident_ids` entry
violated the peer-linkage contract and canonical validation stopped. Revision
416 preserves and corrects that failure.

This correction does not broaden the exact tool view, worker package, provider,
data, application, deployment, release, Pages or protected-ref authority.
