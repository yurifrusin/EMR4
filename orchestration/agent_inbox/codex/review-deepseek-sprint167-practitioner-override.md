# Sprint 167 DeepSeek Review - Practitioner Override Context Threading

**Reviewer:** DeepSeek worker lane  
**Date:** 2026-07-07  
**Verdict:** Accepted - no blocking issues.

## Findings

**Correctness - new-reply-wins practitioner semantics**

The pre-resolution of `practitioner_id` from the current instruction now runs before the clarification merge loop. When it resolves a practitioner such as "Dr Patel", the merge skips `practitioner_id` from the prior context frame while the other threaded fields carry forward unchanged. This matches the intended contract.

**Context frame UUID path preserved**

When the instruction does not name a practitioner and the context frame carries a valid practitioner UUID, the merge path still carries it forward. The UUID fallback through `_context_frame_value` is also preserved for frames where the payload did not already provide the practitioner.

**Warning and assumption propagation correct**

When the pre-resolved practitioner is used, the stored warnings, assumptions, and confidence axis are carried into the response. When pre-resolution returns no practitioner, the fallback chain remains context frame UUID, then diary-context inference, with no new provider/runtime path.

**Gate compliance**

No live provider calls, database writes, memory, RAG, GraphRAG, H-series, or historical diary trove references are introduced. The fixture includes forbidden outcomes for provider calls, appointment writes, and audit writes, and explicitly asserts no appointment or audit writes.

**Test coverage adequate**

The new `interpret_context_practitioner_override.yaml` scenario exercises the missing override path end-to-end with a second practitioner fixture. Existing fixtures continue to cover missing practitioner clarification and first-turn practitioner interpretation.

## Non-Blocking Notes

- `_resolve_practitioner_from_instruction` now performs one practice-scoped practitioner query on interpret turns where the command candidate lacks a practitioner UUID. The table is small and the cost is acceptable.
- A pre-existing runtime isolation test issue on `master` was noted by the worker and is not introduced by Sprint 167.
