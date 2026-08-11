# Ariadne agent error and correction register — revision 251

Date: 2026-08-12

Revision 251 records and corrects AER-0283. The register now contains 283
bounded known incidents with none open.

The first fresh Gemini veto of the CF-D2 anchor-revision correction returned a
nominal pass, zero P0–P2 findings and a clean unchanged worktree. Its own
receipt nevertheless reported a different register test and wider Ruff and
compilation targets than the packet's literal command allowlist. Sol rejected
the decision before diagnostic attempt 002; no Docker, database, provider,
product or external-network operation occurred.

The replacement review must use a fresh project and newly committed exact
HEAD. Its packet enumerates each command as a closed manifest item, and
acceptance will mechanically compare the reported commands with that manifest.
A zero exit code or terminal `pass` cannot cure a substituted or widened
command.

This is further input to the post-CF-D2 workflow diagnosis: independent review
is valuable, but only when its evidence contract is executable and
machine-reconciled. Repeating a prose instruction to follow an exact list is
not an additional safety control.
