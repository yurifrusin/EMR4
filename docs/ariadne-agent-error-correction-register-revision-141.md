# Ariadne agent error and correction register revision 141

Date: 2026-08-09

Status: bounded register correction candidate

Revision 141 adds AER-0166 and brings the register to 166 bounded incidents
with zero open incidents.

## AER-0166 — verifier worktree represented as a handoff workspace

The first JSON-key-order verifier predispatch state included the clean r138
candidate in the generic handoff workspace-assignment fields. The orchestrator
preflight correctly returned `revision_required` because a non-protected
review branch intentionally does not equal `handoff/current`. The launcher
guard stopped before Antigravity or any model call.

The corrected state preserves the exact reviewer branch and HEAD in the five-
source Git evidence and in the separate verifier-worktree preflight, while
leaving handoff workspace assignments empty. Its replacement receipt passed
before the single Gemini 3.6 Flash/high launch. Future verifier dispatches use
handoff workspace-assignment fields only when the active harness contract
actually requires handoff alignment.
