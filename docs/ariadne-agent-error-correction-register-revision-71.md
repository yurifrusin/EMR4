# Ariadne agent-error register revision 71

Date: 2026-08-07

Status: second durability body veto and reviewer command correction preserved

Revision 71 adds AER-0070 and AER-0071.

AER-0070 preserves rejection of exact candidate
`5ea59e14184b26dfa0b8d3a6ebaf28b39c04fb9d`. Its 128-test packet passed, but
fresh manual R1–R4 review found conflict-blind receipt replay, incomplete
registration head/baseline semantics, generation-unjoined retention/key proof
and critical signature/trigger fields still dependent on canonical section
equality. The candidate remains untrusted and the second exact-veto recovery is
the only implementation source for those four surfaces.

AER-0071 separately preserves the reviewer's invalid Boolean spelling
`RUFF_NO_CACHE=1`. Ruff rejected that invocation before analysis. The corrected
`RUFF_NO_CACHE=true` command passed; exact HEAD and worktree remained unchanged.
This process error does not alter or weaken the review findings.

Revision 71 contains 71 bounded incidents. Incident counts remain
workflow-improvement signals only.
