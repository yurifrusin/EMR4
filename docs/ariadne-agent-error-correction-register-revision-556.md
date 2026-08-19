# Ariadne agent-error and correction register — revision 556

Date: 2026-08-19
Timestamp: 2026-08-19T09:49:44.1344800+10:00 (Australia/Brisbane)

## Revision scope

Revision 556 preserves AER-0645. After the live latch was validly blocked at the adoption fork, six focused tests still tried to rebuild from mutable `current.json`; the builder correctly denied every attempt with `active_latch`.

Construction replay now consumes the immutable preplanning `active_operation`. The real runner separately proves that it rejects the blocked latch without changing evidence or report bytes. The register contains 645 incidents, all corrected or contained and none open. Final end-to-end build cost is fifteen reruns.

Repair-only break-even remains two future closeouts. Cumulative break-even, including the predecessor's thirteen sunk reruns, is now four closeouts.

## Prevention

Historical replay consumes immutable operation evidence. Mutable `current.json` is used only for live lifecycle assertions and must fail closed after terminal transition.
