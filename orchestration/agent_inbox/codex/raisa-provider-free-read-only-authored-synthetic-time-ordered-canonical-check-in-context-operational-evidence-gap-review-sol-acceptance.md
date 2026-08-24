# Sol acceptance — time-ordered check-in operational-evidence gap review

Date: 2026-08-24

Timestamp: 2026-08-24T17:10:39.6960019+10:00 (Australia/Brisbane)

Exact reviewed candidate: `7e1b7affc4311faac0116b612b03f54389f046bb`

Decision: `accept_one_narrow_post_proposal_revalidation_successor`

I accept the read-only evidence join at SHA-256
`09be9b9bc9e9a149fee0f1a5da0fc591017bfc7b4a517fda1a0f700003b22d97`.
All five source hashes and full ancestral Git objects match. The 30-case
in-memory matrix was not promoted into physical proof.

Accepted route/database evidence already covers the unchanged default denial,
eligible writes, state and evidence revalidation, replay/conflict/in-progress,
rollback and exact readback. Attempt 008 separately proves rollback and
unknown-response authoritative readback; the restricted PostgreSQL role
attestation separately proves tenant denial. Repeating those tranches would
not add evidence.

Exactly two post-proposal transitions remain without a database-backed route
witness: current Receptionist authority revocation and selected waiting-area
deactivation. One next rehearsal may cover those two and nothing broader. It
does not reopen the 11/0/1 admission matrix or its zero repository
prerequisites.

DeepSeek had negative leverage because no bounded semantic join package could
alter the deterministic result. Gemini was not applicable with neutral
leverage because immutable predicates fully decide the review. Native
subagents had negative leverage at a serial acceptance boundary. GPT Sol owned
the review.

Ten focused and 24 focused-plus-predecessor tests pass; 40 hostile mutations,
Ruff, compileall, no-write replay and diff hygiene pass. No route, database,
runtime, provider, historical data, product source or API Spine artifact was
opened or changed.
