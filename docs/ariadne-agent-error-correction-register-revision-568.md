# Ariadne agent-error and correction register — revision 568

Date: 2026-08-20

Timestamp: 2026-08-20T09:54:56.7001117+10:00 (Australia/Brisbane)

## Revision scope

Revision 568 records four bounded incidents from the DeepSeek native Harness
provider-free required-service injection recovery.

First, the initial controller depended on `LOCALAPPDATA` even though the exact
provider-free pytest wrapper removes it. The independent isolated-worktree
review found seven failures. The corrected resolver retains `LOCALAPPDATA` when
present, otherwise selects the first existing non-symlink user-owned
`AppData/Local/npm-cache` in repository ancestry, and fails closed when no such
candidate exists.

Second, the first verifier manifest selected one accepted predecessor test
whose physical `docs/branding/` assertion is intentionally primary-worktree
only and cannot transfer into a clean Git review worktree. The corrected
manifest excludes only that test, leaves it unchanged, and directly binds both
immutable failed native attempts in the current candidate suite.

Third, the first corrected Gemini project executed all ten commands at exit
zero and produced a substantive pass review, but its structured terminal
envelope inserted `diff` into the reported C10 argv. Exact local admission
rejected the envelope. A fresh project repeated the complete review and
returned the exact manifest argv, 86 passing tests, unchanged HEAD and a clean
worktree.

Fourth, the first live clockwork publication derived the new canonical
register state but the caller had not materialised this required versioned
human-readable companion note. The post-publication suite rejected the
generation and the clockwork restored the preceding generation byte-exactly.
This note and an explicit prepublication companion-artifact check correct that
omission before the next publication.

The clockwork derives the incident identifiers, revision, origin, status,
peer links, counts and pattern report from the semantic observations in the
closeout intent. This document is explanatory evidence and does not replace
the canonical register under
`orchestration/continuity/ariadne-agent-error-register/`.

## Prevention

Provider-free controllers are tested under the exact stripped environment;
verifier manifests classify primary-worktree-only assertions before dispatch;
structured command results remain subject to exact local argv admission; and
every incident-intake closeout checks that its machine-derived versioned
register note exists before canonical publication.
