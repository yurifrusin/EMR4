# A5.1/B4.1 worker pre-dispatch state repair

Date: 2026-08-05

The first deterministic worker pre-dispatch receipt returned
`revision_required` before any worker launch. The runtime-state declarations
used unsupported observation methods for the DeepSeek and Claude transport
adapters and set both exact-source workspace alignment flags false. Both
worktrees were independently observed clean at exact task source
`902040a551668bf8e5a1dd9abaae379224995eec`; no provider/model call or code
change occurred.

Sol changed only those receipt declarations to the accepted adapter method and
exact source/candidate alignment. The protected refs, candidate, worker packets,
data/provider/cost posture and forbidden surfaces are unchanged. The corrected
receipt must pass before either worker starts.
