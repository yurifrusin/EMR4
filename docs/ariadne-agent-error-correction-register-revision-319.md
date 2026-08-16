# Ariadne agent error and correction register — revision 319

Date: 2026-08-17

Timestamp: 2026-08-17T06:47:40.7022740+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 319 records 368 bounded known incidents. No incident is open.

- AER-0368 preserves a recurrence of AER-0365: the first pre-verifier runtime
  placed a tree object ID in the field reserved for resolvable commit-ref
  evidence. The existing fail-closed guard stopped dispatch before any Gemini
  call. The corrected runtime keeps tree binding in the dedicated worktree
  preflight/review evidence and names only commit IDs in the Git-ref field.

The recurrence is workflow evidence, not a product or model-quality defect.
The exact candidate, review worktree and protected refs remained unchanged,
and no database, provider, protected evidence or deployment surface opened.
