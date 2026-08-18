# Ariadne agent error and correction register — revision 372

Date: 2026-08-18

Timestamp: 2026-08-18T10:07:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 372 adds AER-0424. The first Gemini 3.7 Flash/high exact-candidate
veto completed its provider process but returned no schema-admissible decision
envelope. The Antigravity wrapper correctly rejected the non-decision and left
the review worktree unchanged, but its digest-only evidence path covered only
nonzero transport exits. The post-transport parse exception therefore produced
no failure receipt.

The wrapper now writes a sanitized `ariadne.egress-failure-receipt.v1` for
structured-envelope and legacy decision-count failures. It records only
bounded transport/model/worktree metadata and stdout/stderr digests, never raw
provider output. Focused regressions cover missing, duplicate and conflicting
egress while preserving exact candidate identity.

## Population

- incidents: 424;
- corrected or explicitly contained: 424;
- open: 0;
- latest id: `AER-0424`.

No product route, database, provider authority, deployment or protected ref
opened. One fresh same-model retry remains separately gated because the first
attempt yielded no admitted review decision.
