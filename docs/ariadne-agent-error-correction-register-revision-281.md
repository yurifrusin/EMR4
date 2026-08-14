# Ariadne agent error and correction register — revision 281

Date: 2026-08-15

Timestamp: 2026-08-15T06:15:00+10:00 (Australia/Brisbane)

Revision 281 records AER-0320. The register now contains 320 bounded known
incidents, all corrected or contained by an explicit control.

AER-0320 records a rejected pre-verifier runtime state. Sol invented the
parallelism disposition `selected`, supplied the clean verifier worktree using
a generic path/status/head shape instead of the required resource-bound shape,
and populated an assigned-agent id without its matching resource receipt. The
Ariadne preflight stopped the state before any verifier dispatch.

The correction reuses the exact passing pre-verifier vocabulary and structure:
Gemini is `planned`, the worktree receipt names resource, worktree, branch,
exact head and clean state, and the external adapter does not populate the
internal assigned-agent list. The regenerated receipt passed before the single
Gemini call. Register admission also required the new incident's peer list to
remain empty because cross-attempt related links are invalid. The orientation
candidate, product source, protected evidence and protected refs were unchanged.

Future pre-verifier states must be constructed from the last passing exact
analogue and locally admitted before an external verifier is invoked; enum and
workspace receipt shapes must not be inferred.
