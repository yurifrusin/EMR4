# Ariadne agent-error register revision 49

Date: 2026-08-06

Status: migration/transaction architecture plan recovery active

## AER-0051 open

The fresh exact-head plan veto rejected candidate
`bea7d7193503c9176acea24395d3b7727f617454`. The plan did not authenticate the
observer/proofreader packet accepted by the separate coordinator; made exact
redelivery depend on an independently purgeable source row; could not represent
an independent anchor for every advancing checkpoint; omitted the lifecycle
row from the authoritative atomic coordinator effects; and left key schedule
scope ambiguous between one stream and one observer generation.

Sol invoked the plan's existing recovery lease. The recovered candidate adds an
immutable receiver-owned admission bound to actual observer session identity and
exact source membership, receipt/admission-first redelivery, append-only
lifecycle-owned anchors with an anchor-before-next-transition fence, atomic
`DECISION` lifecycle append and exact generation-local key intervals/rotation.
A genuinely fresh exact-head veto is required before plan acceptance.

## AER-0052 corrected

The first reviewer packet recommended `uv run --frozen` despite its read-only
worktree boundary. `uv` unexpectedly created an ignored `.venv` before the
focused test import failed on missing `authlib`. The reviewer self-reported
immediately. The conductor verified the exact owned target under disposable
worktree `r23`, previewed cleanup naming only `.venv/`, removed exactly that
directory, and restored clean exact HEAD. No user-owned untracked file changed.

Fresh read-only reviewer packets must forbid `uv`, `pip` and environment
bootstrap; they may use only an already-proven absolute interpreter or
non-importing/no-conftest static checks, otherwise they stop and report.

Revision 49 contains 52 bounded incidents: 40 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
AER-0051 is the sole open incident. Counts remain workflow-improvement signals
and do not establish model, provider, transport or role causation.
