# Sol acceptance: Ariadne post-compaction active-operation latch

Date: 2026-08-13

Timestamp: 2026-08-13T09:31:31+10:00 (Australia/Brisbane)

Decision: `accepted`

Result: `ariadne_postcompaction_active_operation_latch_pass`

Source: `ac62a6f65612acb624f14b53ba86b1a9dbf72dab`

Reasoning level: bounded workflow continuity control / High

The source is accepted. It adds a closed exact active-operation schema, pure
validator and interruption decision, continuation-receipt projection and
terminal-response guard. It preserves the five-source hierarchy: the latch is
continuity evidence, not authority.

All configured continuation events require the latch. An `in_progress` latch
cannot permit terminal handback, omit its next stage, disable compaction resume
or manufacture a user-attention fork. Side questions and status requests answer
then resume; additions merge then resume; explicit pause/redirect remains
available through a recorded state transition.

The timestamp convention is accepted for all newly authored tranche plans,
threat-model deltas, reports, closeouts, Sol acceptances and Yuri paired
summaries. The final canonical fast profile passes with 193 tests.

This acceptance opens no product surface. It resumes only the already frozen
provider-free read-only status-confirm route-mounting readiness re-review.
